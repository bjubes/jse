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
            print(value)
            value = parse_bash_brackets_value(value)
        else:
            # the user passed {value} and bash has messed with it
            value = ",".join(value)          
            value = "{{{}}}".format(value)
            value = parse_value(value)
    except Exception as err:
        raise EditorError("too many arguments were passed or bash has preprocessed and mangled your input. Try putting VALUE in quotes.") from err
    return value

# takes in elements from bash and returns the value as a parsed python object
# performs a series of checks and passes work to other functions
def parse_bash_brackets_value(elements):
    if any(x[:x.find(',')].count(':')>1 for x in elements):
        # there are subkeys in this object
        elements = [ e[1:-1] for e in elements]
        return [parse_nested_object(elements)]
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
        for obj_a in range(n_attr):
            obj[tree[0][obj_i][0]] = tree[0][obj_i][1]

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
