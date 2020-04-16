
import sys

# use the query to find the sub object we have to modify
def query_object(json,query):
    query = query.replace("]","").replace("[", ".").split(".")
    obj = json
    for k in query[:-1]:
        try:
            obj = obj[k]
        except KeyError as err:
            raise EditorError("'{}' doesn't exist. you can add it with --add".format(k)) from err
        except TypeError:
            try:
                obj = obj[int(k)]
            except IndexError as err:
                raise EditorError("there is no element with index {}. The largest index is {}".format(int(k),len(obj)-1)) from err

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

########## operations ############


def add_func(obj,key,value):
    try:
        obj[key]
        #this object already exists, but if its a list lets auto append
        if type(obj[key]) == list:
            obj[key].append(value)
            return
        #its not a list, so we are editing an existing value
        raise EditorError("'{}' already has a value. Use --edit to modify it".format(key))
    except KeyError:
        # the key doesn't exist. this means add is valid
        obj[key] = value
    except TypeError:
        # this is a list
        if int(key) == len(obj):
            obj.append(value)
        elif int(key) < len(obj):
            raise EditorError("'{}' already has a value. Use --edit to modify it".format(key))
        else:
            raise EditorError("the list only has {} elements. remove the index from your query to add to the end of this list automatically".format(len(obj)))


def edit_func(obj,key,value):
    try:
        if key not in obj:
            if isinstance(obj) == list:
                raise TypeError
            raise EditorError("'{}' doesn't exist. you can add it with --add".format(key))
        obj[key] = value
    except TypeError:
        try:
            obj[int(key)] = value
        except ValueError as err:
            raise EditorError("'{}' doesn't exist. you can add it with --add".format(key)) from err
        except IndexError as err:
            raise EditorError("there is no element with index {}. The largest index is {}".format(int(key),len(obj)-1)) from err

def delete_func(obj,key):
    try:
        del obj[key]
    except KeyError as err:
       raise EditorError("'{}' doesn't exist.".format(key)) from err
    except:
        try:
            del obj[int(key)]
        except IndexError as err:
            if len(obj) == 0:
                raise EditorError("the list is already empty") from err
            raise EditorError("there is no element with index {}. The largest index is {}".format(int(key),len(obj)-1)) from err
        except ValueError as err:
            # this is a list but we gave a non-integer as our key
            if key == '^' or key == 'first':
                del obj[0]
            elif key == '$' or key == 'last':
                del obj[-1]
            else:
                raise EditorError("'{}' is not a valid list index.".format(key)) from err


class EditorError(Exception):
    pass
