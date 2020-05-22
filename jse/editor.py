
import sys
FIRST_EXPR = ['first','^']
LAST_EXPR = ['last','$']
ALL_EXPR = ['all','*']
# use the query to find the sub object we have to modify
# returns an obj and its query OR
# a list of obj-query pairs and None
def query_object(json,query):
    query = query.replace("]","").replace("[", ".").split(".")
    obj = json
    for i,k in enumerate(query[:-1]):
        try:
            obj = obj[k]
        except KeyError as err:
            if k in ALL_EXPR:
                return [query_object(obj,q  + "." +".".join(query[i+1:])) for q in obj.keys()],None
            raise EditorError(f"'{k}' doesn't exist. you can add it with --add") from err
        except TypeError:
            try:
                if k in FIRST_EXPR:
                    k = 0
                elif k in LAST_EXPR:
                    k = -1
                elif k in ALL_EXPR:
                    return [query_object(obj, str(l) + "." +".".join(query[i+1:])) for l in range(len(obj))],None
                obj = obj[int(k)]
            except IndexError as err:
                raise EditorError(f"there is no element with index {k}. The largest index is {len(obj)-1}") from err
    return obj, query[-1]

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
    
    if v[0] == '[' and v[-1] == ']':
        elems = split_on_root(v[1:-1],',')
        return [parse_value(e) for e in elems]

    if v[0] == '{' and v[-1] == '}':
        if len(v.replace(" ","")) == 2:
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

########## operations ############


def add_func(obj,key,value):
    try:
        obj[key]
        #this object already exists, but if its a list lets auto append
        if type(obj[key]) == list:
            obj[key].append(value)
            return
        #its not a list, so we are editing an existing value
        raise EditorError(f"'{key}' already has a value. Use the edit command to modify it")
    except KeyError:
        # the key doesn't exist. this means add is valid
        obj[key] = value
    except TypeError as err:
        # this is a list
        if key.lower() in LAST_EXPR:
            obj.append(value)
            return
        if key.lower() in FIRST_EXPR:
            obj.insert(0,value)
        elif int(key) == len(obj):
            obj.append(value)
        elif int(key) < len(obj):
            raise EditorError(f"'{key}' already has a value. Use the edit command to modify it") from err
        else:
            raise EditorError(f"the list only has {len(obj)} elements. remove the index from your query to add to the end of this list automatically") from err


def edit_func(obj,key,value):
    try:
        if key not in obj:
            if isinstance(obj,list):
                raise TypeError
            raise EditorError(f"'{key}' doesn't exist. you can add it with --add")
        obj[key] = value
    except TypeError:
        try:
            if key.lower() in FIRST_EXPR:
                key = 0
            elif key.lower() in LAST_EXPR:
               key = -1
            elif key.lower() in ALL_EXPR:
                for k in obj.keys():
                    obj[k] = value
                return
            obj[int(key)] = value
        except IndexError as err:
            raise EditorError(f"there is no element with index {key}. The largest index is {len(obj)-1}") from err

def delete_func(obj,key):
    try:
        del obj[key]
    except KeyError as err:
        if key.lower() in ALL_EXPR:
            for k in list(obj.keys()):
                del obj[k]
            return
        raise EditorError(f"'{key}' doesn't exist.") from err
    except:
        try:
            del obj[int(key)]
        except IndexError as err:
            if len(obj) == 0:
                raise EditorError("the list is already empty") from err
            raise EditorError(f"there is no element with index {key}. The largest index is {len(obj)-1}") from err
        except ValueError as err:
            # this is a list but we gave a non-integer as our key
            if key.lower() in FIRST_EXPR:
                del obj[0]
            elif key.lower() in LAST_EXPR:
                del obj[-1]
            elif key.lower() in ALL_EXPR:
                for k in list(obj.keys()):
                    del obj[k]
            else:
                raise EditorError(f"'{key}' is not a valid list index.") from err

class EditorError(Exception):
    pass
