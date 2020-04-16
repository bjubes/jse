#!/usr/bin/env python3
import json
import sys
import click

VERSION = "0.0.5"


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: {}'.format(', '.join(sorted(matches))))

@click.group(cls=AliasedGroup)
@click.argument('file')
@click.pass_context
@click.version_option(version=VERSION)
def jse(ctx,file):
    ctx.obj = file

@jse.command(short_help='add a new element or append to a list')
@click.argument('query')
@click.argument('value', nargs=-1)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.pass_obj
def add(file,query,value,preview):
    value = parse_value_from_bash(value)
    json = load_json(file)
    obj,key = query_object(json,query)
    add_func(obj,key,value)
    if preview:
        print(json)
        return
    save_json(file,json) 

@jse.command(short_help='change an existing key to a new value')
@click.argument('query')
@click.argument('value', nargs=-1)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.pass_obj
def edit(file,query,value,preview):
    value = parse_value_from_bash(value)
    json = load_json(file)
    obj,key = query_object(json,query)
    edit_func(obj,key,value)
    if preview:
        print(json)
        return
    save_json(file,json) 

@jse.command(short_help='delete an element')
@click.argument('query', nargs=-1)
@click.pass_obj
def delete(file,query):
    json = load_json(file)
    for q in query:
        obj,key = query_object(json,q)
        delete_func(obj,key)
    save_json(file,json) 




# values can be corrupted into a list of arguments by bash brace expansion
# this function handles converting value that was passed via the cmdline
# if the value is a string not from the commandline, call parse_value directly.
def parse_value_from_bash(value):
    if len(value) == 1:
        return parse_value(value[0])
    try:
        if all(arg[0] == "[" and arg[-1] == "]" for arg in value):
            #the user has passed [value] and bash has messed with it.
            print(value)
            value = fix_bash_brackets(value)
        else:
            # the user passed {value} and bash has messed with it
            value = ",".join(value)          
            value = "{{{}}}".format(value)
            value = parse_value(value)
    except:
        print_err("too many arguments were passed or bash has preprocessed and mangled your input. Try putting VALUE in quotes.")
    return value

def fix_bash_brackets(elements):
    cnt = len(elements[0].split(','))
    obj_list = []
    for i in range(cnt):
        args = []
        for elem in elements:
            args.append(elem[1:-1].split(',',1)[i])
        # a hack to see when to parse nested vs semetric elements in a list
        key = elements[0].split(':',1)[0][1:]
        if key in elements[1] and (key in elements[len(elements)-2] or key in elements[2]):
            #this is the dot product pattern of semetrical elements
            return parse_brackets_semetric(elements)
        else:
            #nested parsing
            obj = parse_colons(args)
            obj_list.append(obj)
    return obj_list

def parse_brackets_semetric(elements):
    # hardcoded indexes where uniform vectors fall. has to do with
    # where the identity matrix 1s are
    indexes = []
    length = len(elements)
    if length == 4:
        indexes = [0,3]
    if length == 8:
        indexes = [0,7]
    if length == 9:
        indexes = [0,4,8]
    if length == 27:
        indexes = [0,13,26]
    
    selected_elems = [elements[n] for n in indexes]
    elems = [parse_value(s.replace('[', '[{').replace(']','}]').replace(',','},{')) for s in selected_elems]
    combine = list(zip(*elems))
    obj_list = []
    for tup in combine:
        obj = {}
        for o in tup:
            obj[list(o.keys())[0]] = list(o.values())[0]
        obj_list.append(obj)
    return obj_list

def parse_colons(elements):
    print(elements)
    obj = {}
    for elem in elements:
        if ':' in elem:
            k,v = elem.split(':',1)
            if k not in obj:
                obj[k] = parse_value(v)
            else:
                obj[k] = [obj[k],parse_value(v)]
    for k in obj:
        if type(obj[k]) == list:
           obj[k] = parse_colons(obj[k])
    return obj

def load_json(filename):
    with open(filename) as f:
        json_dict = json.load(f)
        return json_dict
          
def save_json(filename, json_obj):
    with open(filename,'w') as f:
        json.dump(json_obj,f,indent=4)

# use the query to find the sub object we have to modify
def query_object(json,query):
    query = query.replace("]","").replace("[", ".").split(".")
    obj = json
    for k in query[:-1]:
        try:
            obj = obj[k]
        except TypeError:
            obj = obj[int(k)]
    return obj, query[-1]

def add_func(obj,key,value):
    try:
        obj[key]
        #this object already exists, but if its a list lets auto append
        if type(obj[key]) == list:
            obj[key].append(value)
            return
        #its not a list, so we are editing an existing value
        print_err("'{}' already has a value. Use --edit to modify it".format(key))
    except KeyError:
        # the key doesn't exist. this means add is valid
        obj[key] = value
    except TypeError:
        # this is a list
        if int(key) == len(obj):
            obj.append(value)

def edit_func(obj,key,value):
    try:
        if key not in obj:
            if isinstance(obj) == list:
                raise TypeError
            print_err("'{}' doesn't exist. you can add it with --add".format(key,obj))
        obj[key] = value
    except TypeError:
        obj[int(key)] = value

def delete_func(obj,key):
    try:
        del obj[key]
    except:
        try:
            del obj[int(key)]
        except IndexError:
            if int(key) == 0:
                print_err("the list is already empty")
            print_err("There is no element with index {}. The largest index is {}".format(int(key),len(obj)-1))
        except ValueError:
            # this is a list but we gave a non-integer as our key
            if key == '^' or key == 'first':
                del obj[0]
            if key == '$' or key == 'last':
                del obj[-1]

# convert any value in string representation into a python object or standard type
def parse_value(v):
    if v.isdigit():
        return int(v)
    try:
        return float(v)
    except ValueError:
        pass
    
    v = v.strip()
    if v.lower() == "true":
        return True
    if v.lower()== "false":
        return False
    if v.lower() == "null":
        return None
    
    if v[0] is '[' and v[-1] is ']':
        elems = split_on_root(v[1:-1],',')
        return [parse_value(e) for e in elems]

    if v[0] is '{' and v[-1] is '}':
        if len(v.replace(" ","")) ==2:
            return {}
        obj = {}
        elems = split_on_root(v[1:-1],',')
        for elem in elems:
            key,value = elem.split(":",1)
            obj[key] = parse_value(value)
        return obj
        
    return str(v)

# splits a string using delim, but ignores it inside brackets and braces
def split_on_root(string, delim, openers="[{", closers="}]"):
    elems = []
    ptr = 0
    depth = 0
    for i,c in enumerate(string):
        if c == delim and depth == 0:
            elems.append(string[ptr:i])
            ptr = i+1
        if c in openers:
            depth += 1
        if c in closers:
            depth -= 1
    if ptr != len(string):
        elems.append(string[ptr:])
    return elems


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


if __name__ == '__main__':
    jse()