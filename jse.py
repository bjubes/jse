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
    args = parser.parse_args()

    if args.delete:
        json = load_json(args.file)
        for key in args.delete:
            json = operate_on_key(json,key,None,delete_func)
        save_json(args.file,json) 
    elif args.add:
        parse_key_value(args,args.add,"add",add_func,create_keys=True)
    elif args.edit:
        parse_key_value(args,args.edit,"edit",edit_func,create_keys=False)
    else:
        print_err("must select an operation. use --help to see options")

def parse_key_value(args,fn_args,name,func,create_keys):
    if len(fn_args) < 2:
        print_err(name,"takes a key and a value")
        return
    key = fn_args[0]
    value = fn_args[1]
    if len(fn_args) is not 2:
        # this happens when you pass an obj as {} directly in bash
       value = ",".join(fn_args[1:])          
       value = "{{{}}}".format(value)
    value = typed_value(value)
    obj = load_json(args.file)
    obj = operate_on_key(obj,key,value,func,create_keys=create_keys)
    save_json(args.file,obj)


def load_json(filename):
    with open(filename) as f:
        json_dict = json.load(f)
        return json_dict
          
def save_json(filename, json_obj):
    with open(filename,'w') as f:
        json.dump(json_obj,f,indent=4)
          
def operate_on_key(json,key,value,func,create_keys=True):
    query = key.replace("]","").replace("[", ".").split(".")
    if len(query) == 1:
        if not create_keys and key not in json:
            print_err("Key '{}' does not exist".format(key))
            return json
        json[key] = value
    obj = json
    for k in query[:-1]:
        try:
            obj = obj[k]
        except TypeError:
            obj = obj[int(k)]
    func(obj,query[-1],value)
    return json

def add_func(obj,key,value):
    try:
        if isinstance(obj[key],list):
            length = len(obj[key])
            obj[key].append(None)
            obj = obj[key]
            key = length
        else:
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
        del obj[int(key)]


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
        obj = {}
        if len(v.replace(" ","")) ==2:
            return {}
        elems = split_on_root(v[1:-1],',')
        for e in elems:
            key,value = e.split(":",1)
            obj[key] = typed_value(value)
        return obj
        
    return str(v)

# splits a string using delim, but ignores it inside brackets and braces
def split_on_root(string, delim, openers="[{", closers="}]"):
    ptr = 0
    elems = []
    stack = []
    for i,c in enumerate(string):
        if c == delim and len(stack) == 0:
            elems.append(string[ptr:i])
            ptr = i+1
        if c in openers:
            stack.append(c)
        if c in closers:
            stack.pop()
    if ptr != len(string):
        elems.append(string[ptr:])
    return elems


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    main()
