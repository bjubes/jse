#!/usr/bin/env python3
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the JSON file to use")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e","--edit", nargs='*', help="change the value of the json element")
    group.add_argument("-d","--delete", nargs='*', help="remove the json element")
    group.add_argument("-a","--add", nargs='*', help="add a json element")
    parser.add_argument("--preview",action="store_true",help="preview file changes without saving to disk")
    args = parser.parse_args()

    if args.delete:
        json = load_json(args.file)
        for key in args.delete:
            json = operate_on_key(json,key,None,delete_func)
        save_json(args.file,json) 
    elif args.add:
        parse_query(args,args.add,"add",add_func,create_keys=True)
    elif args.edit:
        parse_query(args,args.edit,"edit",edit_func,create_keys=False)
    else:
        print_err("must select an operation. use --help to see options")

def parse_query(args,fn_args,name,func,create_keys):
    if len(fn_args) < 2:
        print_err(name,"takes a key and a value")
        return
    query = fn_args[0]
    value = fn_args[1]
    if len(fn_args) is not 2:
        # this happens when you pass an obj as {} directly in bash
       value = ",".join(fn_args[1:])          
       value = "{{{}}}".format(value)
    value = typed_value(value)
    obj = load_json(args.file)
    obj = operate_on_key(obj,query,value,func,create_keys=create_keys)
    if args.preview:
        print(obj)
        return
    save_json(args.file,obj)


def load_json(filename):
    with open(filename) as f:
        json_dict = json.load(f)
        return json_dict
          
def save_json(filename, json_obj):
    with open(filename,'w') as f:
        json.dump(json_obj,f,indent=4)
          
def operate_on_key(json,key,value,func,create_keys=True):
    try:
        obj,query = query_object(json,key)
    except KeyError:
        if create_keys or not isinstance(json[key],list) :
            json[key] = value
            obj,query = query_object(json,key)

    func(obj,query,value)
    return json

def query_object(json,query):
    query = query.replace("]","").replace("[", ".").split(".")
    if len(query) == 1:
        if query[0] not in json:
            raise KeyError("Key '{}' does not exist".format(query[0]))
    obj = json
    for k in query[:-1]:
        try:
            obj = obj[k]
        except TypeError:
            obj = obj[int(k)]
    return obj, query[-1]

def add_func(obj,key,value):
    try:
        if isinstance(obj[key],list):
            # object is not a list, but value is
            # add dummy entry to overwrite later
            length = len(obj[key])
            obj[key].append(None)
            obj = obj[key]
            key = length
        elif isinstance(obj[key],dict):
            # add our entry to the existing dictionary
            value.update(obj[key])

        else:
            # neither object  nor value are lists,
            # so just make a dummy entry
            obj[key] = None

    # obj is a list
    except TypeError:
        length = len(obj)
        if length > int(key):
            print_err("index {} already exists".format(key))
            return
        if int(key) is not length:
            print_err("The list element must be at index",length)
            return
        obj.append(None)
    edit_func(obj,key,value)

def edit_func(obj,key,value):
    try:
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
            print_err("There is no element with index",int(key))

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
