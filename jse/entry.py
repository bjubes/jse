#!/usr/bin/env python3
import argparse
import json
import sys


class JSONEditor():

    def __init__(self):
        parser = argparse.ArgumentParser(
            usage='''jse <file> <command> <query> <value>
   
commands:
   e, edit     edit the queried key to a new value
   a, add      add a new key-value or append to an existing key
   d, delete   delete the key and associated value
''') 
        parser.add_argument('file')
        parser.add_argument('command')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:3])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()
    
    add_desc = "add a new key-value or append to an existing key"
    
    def add(self):
        parser = argparse.ArgumentParser(
            description=JSONEditor.add_desc,
            usage='''jse <file> add <query> <value>
''')
        parser.add_argument('query')
        parser.add_argument('value',nargs='+')
        args = parser.parse_args(sys.argv[3:])

        print("query", args.query)
        print("value", args.value)

def main():
   
    parser.add_argument("file", help="the JSON file to use")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e","--edit", nargs='*', help="change the value of the json element")
    group.add_argument("-a","--add", nargs='*', help="add a json element")
    group.add_argument("-d","--delete", nargs='*', help="remove the json element")
    parser.add_argument("--preview",action="store_true",help="preview file changes without saving to disk")
    args = parser.parse_args()

    if args.delete:
        json = load_json(args.file)
        for query in args.delete:
            obj,key = query_object(json,query)
            delete_func(obj,key)
        save_json(args.file,json) 
    elif args.add:
        query, value = parse_query(args,args.add,"add")
        json = load_json(args.file)
        obj,key = query_object(json,query)
        add_func(obj,key,value)
        save_json(args.file,json) 
    elif args.edit:
        query, value = parse_query(args,args.edit,"edit")
        json = load_json(args.file)
        obj,key = query_object(json,query)
        edit_func(obj,key,value)
        save_json(args.file,json) 
    else:
        print_err("must select an operation. use --help to see options")

# parses cmd line args and loads and alters the json object
def parse_query(args,fn_args,name):
    if len(fn_args) < 2:
        print_err(name,"takes a key and a value")
        return
    query = fn_args[0]
    value = fn_args[1]
    if len(fn_args) is not 2:
        try:
            if all(arg[0] == "[" and arg[-1] == "]" for arg in fn_args[1:]):
                #the user has passed [value] and bash has messed with it.
                print(fn_args[1:])
                value = fix_bash_brackets(fn_args[1:])
            else:
                # the user passed {value} and bash has messed with it
                value = ",".join(fn_args[1:])          
                value = "{{{}}}".format(value)
                value = parse_value(value)
        except:
            print_err("either you passed too many arguments or bash has preprocessed and mangled your input. Try putting your value in quotes.")
    else:
        value = parse_value(value)
    return query, value

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

if __name__ == "__main__":
   JSONEditor()
