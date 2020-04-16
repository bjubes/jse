
from .editor import *

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
