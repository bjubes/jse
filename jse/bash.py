import math

from .editor import *

# values can be corrupted into a list of arguments by bash brace expansion
# this function handles converting value that was passed via the cmdline
# if the value is a string not from the commandline, call parse_value directly.
def parse_value_from_bash(value):
    if len(value) == 1:
        return parse_value(value[0])
    try:
        if all(arg[0] == "[" and arg[-1] == "]" for arg in value):
            # the user has passed [value] and bash has messed with it.
            return parse_bash_brackets_value(value)
        else:
            # the user passed {value} and bash has messed with it
            val = ",".join(value)          
            val = f"{{{val}}}"
            return parse_value(val)
    except Exception as err:
        if not isinstance(value,str) and any(v == '=' for v in value):
            raise EditorError("do not use '=' when assigning a key to a value") from err
        raise EditorError("too many arguments were passed or bash has preprocessed and mangled your input. Try putting VALUE in quotes.") from err

# takes in elements from bash and returns the value as a parsed python object
# performs a series of checks and passes work to other functions
def parse_bash_brackets_value(elements):
    if any(x[:x.find(',')].count(':')>1 for x in elements):
        # there are subkeys in this object
        return parse_nested_object_list(elements)
    elif all(x.count(',') == 0 for x in elements):
        # no commas in any element means there is only one element in the list
        return parse_split_object(elements)
    else:
        return parse_brackets_semetric(elements)

def parse_split_object(attrs):
    # the object has been split, so {a:1,b:2} is now
    # [a:1]     [b:2]
    obj = {}
    for a in attrs:
        a = a[1:-1]
        k,v = a.split(":",1)
        obj[k] = parse_value(v)
    return [obj]

# given a bash expanded list, determine how many objects were passed and how many
# elements each object had. assumes all elements were of the same attr length
def get_obj_attr_count(elements):
    num_obj = elements[0].count(",") + 1
    #length = num_attrs^ num_obj
    num_attrs = math.log(len(elements)) / math.log(num_obj)
    return num_obj,int(round(num_attrs))


def parse_brackets_semetric(elements):
    n_obj,n_attr = get_obj_attr_count(elements)
    tree = []
    for e in elements:
        subobjs = e[1:-1].split(',')
        elem = []
        for s in subobjs:
            kvp = s.split(':')
            elem.append(kvp)
        tree.append(elem)
    print(tree)

    fixed_input = []
    for obj_i in range(n_obj):
        obj = {}
        for atr_i in range(n_attr):
            # rem_obj is how many objects 
            tree_index = atr_i*n_attr**((n_obj-1-obj_i))
            k = tree[tree_index][obj_i][0] 
            v = tree[tree_index][obj_i][1]
            obj[k] = parse_value(v)
        fixed_input.append(obj)
    return fixed_input

# parses a list of nested objects, assuming they have the same keys
# it is not possibly (to my knowledge) to parse if the first key at least is not 
# repeated in each object
def parse_nested_object_list(elements):
    fixed_list = []
    elems = []
    for e in elements:
        elem = e
        if e[0] == '[':
            elem = elem[1:]
        if e[-1] == ']' or e[-1] ==',':
            elem = elem[:-1]
        elems.append(elem)
    print(elems)
    ptr = 0
    key = None
    for i,e in enumerate(elems):
        if key == None:
            key = e.split(':',1)[0]
        elif e.split(':',1)[0] == key:
            fixed_list.append(parse_nested_object(elems[ptr:i]))
            ptr = i
    fixed_list.append(parse_nested_object(elems[ptr:]))
    return fixed_list

def parse_nested_object(elements):
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
           obj[k] = parse_nested_object(obj[k])
    return obj
