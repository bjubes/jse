import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from jse.entry import *
import pytest

########## typed_value ##########

def test_basic_types_value():
    assert parse_value("str") == "str"
    assert parse_value("32") == 32
    assert parse_value("12.34") == 12.34
    assert parse_value("true") == True
    assert parse_value("false") == False
    assert parse_value("null") == None
    
def test_basic_type_types():
    assert type(parse_value("32")) == int
    assert type(parse_value("str")) == str
    assert type(parse_value("12.34")) == float
    assert type(parse_value("true")) == bool
    assert type(parse_value("false")) == bool
    assert type(parse_value("null")) == type(None)


def test_simple_object():
    d = parse_value("{ key:value }")
    assert type(d) == dict
    d == {"key":"value"}

    d = parse_value(" { a : 23 } ")
    assert type(d) == dict
    d == {"a":23}

def test_nested_object():
    d = parse_value("{root:{subkey:val}}")
    assert type(d) == dict
    assert d == {"root":{"subkey":"val"}}

def test_many_objects():
    d = parse_value("{x:{a:b},y:{c:d}}")
    assert len(d) == 2
    assert d["x"] == {"a":"b"}
    assert d["y"] == {"c":"d"}

    d = parse_value("[{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}]")
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
