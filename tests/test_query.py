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

def test_first_last_list_query():
    obj = {'l':[{'key':3},{'key':-1},{'key':4}]}
    for exp in [('^','$'),('first','last'),("0","-1")]:
        first,last = exp
        subobj,key = query_object(obj,'l.{}.key'.format(first))
        assert key == 'key'
        assert subobj == {'key':3}

        subobj,key = query_object(obj,'l.{}.key'.format(last))
        assert key == 'key'
        assert subobj == {'key':4}

def test_all_query_basic_dict():
    obj = {'a': {
        'ah':{'inner':1},
        'b':{'inner':2},
        'c':{'inner':3}
    }}
    pairs, noneval = query_object(obj,'a.*.inner')
    assert noneval == None
    assert pairs[0] == ({'inner':1}, 'inner')
    assert pairs[1] == ({'inner':2}, 'inner')
    assert pairs[2] == ({'inner':3}, 'inner')

def test_all_query_basic_list():
    obj = {'a': [
        {'inner':1},
        {'inner':2},
        {'inner':3}]
    }
    pairs, noneval = query_object(obj,'a.*.inner')
    assert noneval == None
    assert pairs[0] == ({'inner':1}, 'inner')
    assert pairs[1] == ({'inner':2}, 'inner')
    assert pairs[2] == ({'inner':3}, 'inner')

