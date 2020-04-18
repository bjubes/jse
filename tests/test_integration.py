import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from jse.editor import *
from jse.bash import *
import pytest


def test_basic_edit():
    obj = {'a': 'b'}
    query = 'a'
    value = 'x'
    subobj,key = query_object(obj,query)
    edit_func(subobj,key,value)
    assert obj == {'a': 'x'}


def test_basic_add():
    obj = {'a': 'b'}
    query = 'c'
    value = 'x'
    subobj,key = query_object(obj,query)
    add_func(subobj,key,value)
    assert obj == {'a': 'b', 'c': 'x'}


def test_list_add_auto_index():
    listname = "mylist"
    obj = {listname: []}
    value = 'x'
    subobj,key = query_object(obj,listname)
    add_func(subobj,key,value)
    assert obj == {listname: [value]}


def test_list_add_manual_index():
    listname = "mylist"
    obj = {listname: []}
    query = listname + ".0"
    value = 'x'
    subobj,key = query_object(obj,query)
    add_func(subobj,key,value)
    assert obj == {listname: [value]}


def test_obj_add():
    obj = {
        "my_obj": {}
    }
    query = "my_obj.name"
    value = "waldo"
    func = add_func
    subobj,key = query_object(obj,query)
    add_func(subobj,key,value)
    assert obj == {
        "my_obj": {
            "name": "waldo"
        }
    }


def test_obj_add_example():
    obj = {}
    query = "highscore"
    value = "[{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}]"
    value = parse_value(value)
    subobj,key = query_object(obj,query)
    add_func(subobj,key,value)

    assert obj == {
        "highscore": [
            {
                "score": 32.5,
                "user": "bob",
                "metadata": {
                    "ip": "192.168.1.102",
                    "client": "firefox"
                }
            }, {}
        ]
    }


def test_delete():
    obj = {
        "users": [
            {"id": 1, "name": "mike"},
            {"id": 2, "name": "jon"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }
    subobj,key = query_object(obj,"users.1")
    delete_func(subobj,key)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }
    subobj,key = query_object(obj,"map")
    delete_func(subobj,key)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"}
        ]
    }

def test_list_regex_delete():
    for first,last in zip(FIRST_EXPR,LAST_EXPR):
        obj = {
            "users": [
                {"id": 1, "name": "mike"},
                {"id":7,"name":"paul"},
                {"id":6,"name":"craig"},
                {"id": 2, "name": "jon"}
            ],
            "map": {
                "a": 3,
                "x": 9
            }
        }
        # delete last entry in list
        subobj,key = query_object(obj,"users." + last)
        delete_func(subobj,key)
        assert obj == {
            "users": [
                {"id": 1, "name": "mike"},
                {"id":7,"name":"paul"},        
                {"id":6,"name":"craig"}
            ],
            "map": {
                "a": 3,
                "x": 9
            }
        }
        # delete first entry in list
        subobj,key = query_object(obj,"users." + first)
        delete_func(subobj,key)     
        assert obj == {
            "users": [
                {"id":7,"name":"paul"},
                {"id":6,"name":"craig"}
            ],
            "map": {
                "a": 3,
                "x": 9
            }
        }
    

def test_add_existing_key():
    with pytest.raises(EditorError) as err :
        obj = {'nameofthekey': 'b'}
        subobj,key = query_object(obj,"nameofthekey")
        add_func(subobj,key,"value")
    assert "nameofthekey" in str(err.value)


def test_edit_non_existing_key():
    with pytest.raises(EditorError) as err:
        obj = {'a': 'b'}
        subobj,key = query_object(obj,"nameofthekey")
        edit_func(subobj,key,"new value")
    assert "nameofthekey" in str(err.value)


def test_delete_non_existing_key():
    obj = {'a': {'sub1':0,'sub2':1}}

    with pytest.raises(EditorError) as err:
        subobj,key = query_object(obj,"nameofthekey")
        delete_func(subobj,key)
    assert "nameofthekey" in str(err.value)

    with pytest.raises(EditorError) as err:
        subobj,key = query_object(obj,"a.nameofsubkey")
        edit_func(subobj,key,"new value")
    assert "nameofsubkey" in str(err.value)


def test_delete_list_errors():
    obj = {
        'a' : [
            1,2,3
        ],
        'listname':[]
    }
    # bad regex or non-integer key
    with pytest.raises(EditorError) as err:
        subobj,key = query_object(obj,"a.badregex")
        delete_func(subobj,key)
    assert "badregex" in str(err.value)

    # indexing on empty list
    with pytest.raises(EditorError) as err:
        subobj,key = query_object(obj,"listname.3")
        delete_func(subobj,key)
    assert "empty" in str(err.value)

    with pytest.raises(EditorError) as err:
        subobj,key = query_object(obj,"listname.0")
        delete_func(subobj,key)
    assert "empty" in str(err.value)

    # index out of bounds
    with pytest.raises(EditorError) as err:
        subobj,key = query_object(obj,"a.3")
        delete_func(subobj,key)
    assert "index" in str(err.value)

def test_errors_on_adding_list():
    obj = {'list': [0,1,2]}

    # add beyond range
    with pytest.raises(EditorError) as err :
        subobj,key = query_object(obj,"list.5")
        add_func(subobj,key,"value")

    # add existing value
    with pytest.raises(EditorError) as err :
        subobj,key = query_object(obj,"list.1")
        add_func(subobj,key,"value")
    assert "has a value" in str(err.value)

def test_regex_add():
    for first,last in zip(FIRST_EXPR,LAST_EXPR):
        obj = {'l':[3,4,5]}
        subobj,key = query_object(obj,"l."+last)
        add_func(subobj,key,6)
        assert obj == {'l':[3,4,5,6]}

        subobj,key = query_object(obj,"l."+first)
        add_func(subobj,key,2)
        assert obj == {'l':[2,3,4,5,6]}

def test_regex_edit():
    for first,last in zip(FIRST_EXPR,LAST_EXPR):
        obj = {'l':[3,4,5]}
        subobj,key = query_object(obj,"l."+last)
        edit_func(subobj,key,6)
        assert obj == {'l':[3,4,6]}

        subobj,key = query_object(obj,"l."+first)
        edit_func(subobj,key,2)
        assert obj == {'l':[2,4,6]}