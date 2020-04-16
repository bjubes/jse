import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from jse.editor import *
import pytest

def test_basic_query():
    obj = {'a':3}
    subobj,key = query_object(obj,"a")
    assert key == 'a'
    assert subobj == obj

def test_nested_query():
    obj = {'a':{'b':3}}
    subobj,key = query_object(obj,"a.b")
    assert key == 'b'
    assert subobj == {'b':3}

def test_unkown_end_key_query():
    obj = {'a':{'b':3}}
    subobj,key = query_object(obj,'a.newkey')
    assert key == 'newkey'
    assert subobj == {'b':3}

def test_bad_query():
    with pytest.raises(EditorError) as err:
        obj = {'a':{'b':3}}
        query_object(obj,'badkey.not-as-tail')
    assert 'badkey' in str(err.value)

def test_bad_list_query():
    with pytest.raises(EditorError) as err:
        obj = {'a':[{},{}]}
        query_object(obj,'a.3.object')
    assert '3' in str(err.value)
