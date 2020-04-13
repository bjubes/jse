from jse import *
import pytest


def test_basic_edit():
    obj = {'a': 'b'}
    query = 'a'
    value = 'x'
    func = edit_func
    operate_on_key(obj, query, value, func)
    assert obj == {'a': 'x'}


def test_basic_add():
    obj = {'a': 'b'}
    query = 'c'
    value = 'x'
    func = add_func
    operate_on_key(obj, query, value, func)
    assert obj == {'a': 'b', 'c': 'x'}


def test_list_add_auto_index():
    listname = "mylist"
    obj = {listname: []}
    value = 'x'
    func = add_func
    operate_on_key(obj, listname, value, func)
    assert obj == {listname: [value]}


def test_list_add_manual_index():
    listname = "mylist"
    obj = {listname: []}
    query = listname + ".0"
    value = 'x'
    func = add_func
    operate_on_key(obj, query, value, func)
    assert obj == {listname: [value]}


def test_obj_add():
    obj = {
        "my_obj": {}
    }
    query = "my_obj.name"
    value = "waldo"
    func = add_func
    operate_on_key(obj, query, value, func)
    assert obj == {
        "my_obj": {
            "name": "waldo"
        }
    }


def test_obj_add_example():
    obj = {}
    query = "highscore"
    value = "[{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}]"
    value = typed_value(value)
    func = add_func
    operate_on_key(obj, query, value, func)

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

    operate_on_key(obj, "users.1", None, delete_func)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }
    operate_on_key(obj, "map", None, delete_func)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"}
        ]
    }

def test_list_regex_delete():
    for exp in [('^','$'),('first','last')]:
        first = exp[0]
        last = exp[1]
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
        operate_on_key(obj,"users." + last,None,delete_func)
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
        operate_on_key(obj,"users."+first,None,delete_func)
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


# todo - test error handling and seperate exit from error states
