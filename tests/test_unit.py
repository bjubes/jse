from jse.jse import *
import pytest

########## typed_value ##########

def test_basic_types_value():
    assert typed_value("str") == "str"
    assert typed_value("32") == 32
    assert typed_value("12.34") == 12.34
    assert typed_value("true") == True
    assert typed_value("false") == False
    assert typed_value("null") == None
    
def test_basic_type_types():
    assert type(typed_value("32")) == int
    assert type(typed_value("str")) == str
    assert type(typed_value("12.34")) == float
    assert type(typed_value("true")) == bool
    assert type(typed_value("false")) == bool
    assert type(typed_value("null")) == type(None)


def test_simple_object():
    d = typed_value("{ key:value }")
    assert type(d) == dict
    d == {"key":"value"}

    d = typed_value(" { a : 23 } ")
    assert type(d) == dict
    d == {"a":23}

def test_nested_object():
    d = typed_value("{root:{subkey:val}}")
    assert type(d) == dict
    assert d == {"root":{"subkey":"val"}}

def test_many_objects():
    d = typed_value("{x:{a:b},y:{c:d}}")
    assert len(d) == 2
    assert d["x"] == {"a":"b"}
    assert d["y"] == {"c":"d"}

    d = typed_value("[{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}]")
    assert len(d) == 2
    assert d[1] == {}
    assert d[0] == {
                "score":32.5,
                "user": "bob",
                "metadata": {
                    "ip":"192.168.1.102",
                    "client":"firefox"
                }
            }

########## split_on_root ##########

def test_split_on_root_basic():
    strs = ["a:b,c:d","1,235,2346fds,90 j,dfs","*,234>,29,0"]
    for s in strs:
        assert split_on_root(s,",") == s.split(",")
    
    assert split_on_root(strs[0],":") == strs[0].split(":")

def test_split_on_root_not_nested():
    cases = {
        "a:b,c:{d,e}":["a:b","c:{d,e}"],
        "a:{d,c},b:{as,de},[]": ["a:{d,c}","b:{as,de}","[]"],
        "a:[b,{a}],n:3,x:null,d:{a,b,[]}": ["a:[b,{a}]","n:3","x:null","d:{a,b,[]}"]
    }

    for inp,out in cases.items():
        assert split_on_root(inp,",") == out


def test_split_on_root_nested():
    cases = {
        "a:b,c:{d,[e,f,g],n}":["a:b","c:{d,[e,f,g],n}"],
        "a:{d,[c]},b:{as,de,{a,b,c,[1,2]}},a:[{},{{{}}}]": ["a:{d,[c]}","b:{as,de,{a,b,c,[1,2]}}","a:[{},{{{}}}]"],
        "{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}": ["{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}","{}"]
    }

    for inp,out in cases.items():
        assert split_on_root(inp,",") == out


########## fix_bash_brackets ##########

def test_fix_bash_brackets_nested():
    #input:  [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}]
    corrupted_input = ['[score:32.5]', '[user:bob]', '[metadata:ip:192.168.1.102]', '[metadata:client:firefox]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [{'user':'bob',
                     'score': 32.5,
                     'metadata':{
                         'ip':'192.168.1.102',
                         'client':'firefox'
                     }}]

def test_fix_bash_brackets_symetric():
    #input: [{name:bob,id:1},{name:steve,id:3}, {name:ted,id:5}]
    corrupted_input = ['[name:bob,name:steve,name:ted]', '[name:bob,name:steve,id:5]', '[name:bob,name:steve,g:6]', '[name:bob,id:3,name:ted]', '[name:bob,id:3,id:5]', '[name:bob,id:3,g:6]', '[name:bob,g:4,name:ted]', '[name:bob,g:4,id:5]', '[name:bob,g:4,g:6]', '[id:1,name:steve,name:ted]', '[id:1,name:steve,id:5]', '[id:1,name:steve,g:6]', '[id:1,id:3,name:ted]', '[id:1,id:3,id:5]', '[id:1,id:3,g:6]', '[id:1,g:4,name:ted]', '[id:1,g:4,id:5]', '[id:1,g:4,g:6]', '[g:2,name:steve,name:ted]', '[g:2,name:steve,id:5]', '[g:2,name:steve,g:6]', '[g:2,id:3,name:ted]', '[g:2,id:3,id:5]', '[g:2,id:3,g:6]', '[g:2,g:4,name:ted]', '[g:2,g:4,id:5]', '[g:2,g:4,g:6]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {'name':'bob','id':1,'g':2},
        {'name':'steve','id':3, 'g':4},
        {'name':'ted','id':5, 'g':6}
    ]

    #input: [{name:bob,id:1,x:3},{name:steve,id:3,x:5}]
    corrupted_input = ['[name:bob,name:steve]', '[name:bob,id:3]', '[name:bob,x:5]', '[id:1,name:steve]', '[id:1,id:3]', '[id:1,x:5]', '[x:3,name:steve]', '[x:3,id:3]', '[x:3,x:5]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {'name':'bob','id':1,'x':3},
        {'name':'steve','id':3, 'x':5},
    ]

    #input: [{name:bob,id:1},{name:steve,id:3}]
    corrupted_input = ['[name:bob,name:steve]', '[name:bob,id:3]', '[id:1,name:steve]', '[id:1,id:3]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {'name':'bob','id':1,},
        {'name':'steve','id':3}
    ]

    #input:  [{name:bob,id:1},{name:steve,id:3},{name:ted,id:5}]
    corrupted_input = ['[name:bob,name:steve,name:ted]', '[name:bob,name:steve,id:5]', '[name:bob,id:3,name:ted]', '[name:bob,id:3,id:5]', '[id:1,name:steve,name:ted]', '[id:1,name:steve,id:5]', '[id:1,id:3,name:ted]', '[id:1,id:3,id:5]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {'name':'bob','id':1,},
        {'name':'steve','id':3},
        {'name':'ted','id':5}
    ]



