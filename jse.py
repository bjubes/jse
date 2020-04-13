#!/usr/bin/env python3
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the JSON file to use")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e","--edit", nargs='*', help="change the value of the json element")
    group.add_argument("-a","--add", nargs='*', help="add a json element")
    group.add_argument("-d","--delete", nargs='*', help="remove the json element")
    parser.add_argument("--preview",action="store_true",help="preview file changes without saving to disk")
    args = parser.parse_args()

    if args.delete:
        json = load_json(args.file)
        for key in args.delete:
            json = operate_on_key(json,key,None,delete_func)
        save_json(args.file,json) 
    elif args.add:
        parse_query(args,args.add,"add",add_func)
    elif args.edit:
        parse_query(args,args.edit,"edit",edit_func)
    else:
        print_err("must select an operation. use --help to see options")

# parses cmd line args and loads and alters the json object
def parse_query(args,fn_args,name,func):
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
                value = typed_value(value)
        except:
            print_err("either you passed too many arguments or bash has preprocessed and mangled your input. Try putting your value in quotes.")
    else:
        value = typed_value(value)
    obj = load_json(args.file)
    obj = operate_on_key(obj,query,value,func)
    if args.preview:
        return
    save_json(args.file,obj)

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
    elems = [typed_value(s.replace('[', '[{').replace(']','}]').replace(',','},{')) for s in selected_elems]
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
                obj[k] = typed_value(v)
            else:
                obj[k] = [obj[k],typed_value(v)]
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
          
def operate_on_key(json,query,value,func):
    try:
        obj,key = query_object(json,query)
    except KeyError:
       print("key error in query_object")

    # do the requested operation based on mode (add,edit,delete)
    func(obj,key,value)
    return json

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

def delete_func(obj,key,*ignored):
    try:
        del obj[key]
    except:
        try:
            del obj[int(key)]
        except IndexError:
            if int(key) == 0:
                print_err("the list is already empty")
            print_err("There is no element with index {}. The largest index is {}".format(int(key),len(obj)-1))

def typed_value(v):
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
        return [typed_value(e) for e in elems]

    if v[0] is '{' and v[-1] is '}':
        if len(v.replace(" ","")) ==2:
            return {}
        obj = {}
        elems = split_on_root(v[1:-1],',')
        for elem in elems:
            key,value = elem.split(":",1)
            obj[key] = typed_value(value)
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
    main()
