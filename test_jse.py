from jse import *
import pytest


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
    }

    for inp,out in cases.items():
        assert split_on_root(inp,",") == out