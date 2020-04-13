from jse import *
import pytest


def test_basic_edit():
    json_obj = {'a': 'b'}
    query = 'a'
    value = 'x'
    func = edit_func
    obj = operate_on_key(json_obj, query, value, func)
    assert obj == {'a': 'x'}


def test_basic_add():
    json_obj = {'a': 'b'}
    query = 'c'
    value = 'x'
    func = add_func
    obj = operate_on_key(json_obj, query, value, func)
    assert obj == {'a': 'b', 'c': 'x'}


def test_list_add_auto_index():
    listname = "mylist"
    json_obj = {listname: []}
    value = 'x'
    func = add_func
    obj = operate_on_key(json_obj, listname, value, func)
    assert obj == {listname: [value]}


def test_list_add_manual_index():
    listname = "mylist"
    json_obj = {listname: []}
    query = listname + ".0"
    value = 'x'
    func = add_func
    obj = operate_on_key(json_obj, query, value, func)
    assert obj == {listname: [value]}


def test_obj_add():
    json_obj = {
        "my_obj": {}
    }
    query = "my_obj.name"
    value = "waldo"
    func = add_func
    obj = operate_on_key(json_obj, query, value, func)
    assert obj == {
        "my_obj": {
            "name": "waldo"
        }
    }


def test_obj_add_example():
    json_obj = {}
    query = "highscore"
    value = "[{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}]"
    value = typed_value(value)
    func = add_func
    obj = operate_on_key(json_obj, query, value, func)

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
    json_obj = {
        "users": [
            {"id": 1, "name": "mike"},
            {"id": 2, "name": "jon"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }

    obj = operate_on_key(json_obj, "users.1", None, delete_func)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }
    obj = operate_on_key(obj, "map", None, delete_func)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"}
        ]
    }

def test_list_regex_delete():
    json_obj = {
        "users": [
            {"id": 1, "name": "mike"},
            {"id":7,"name":"paul"},
            {"id": 2, "name": "jon"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }
    # delete last entry in list
    obj = operate_on_key(json_obj,"users.$",None,delete_func)
    assert obj == {
        "users": [
            {"id": 1, "name": "mike"},
            {"id":7,"name":"paul"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }
    obj = operate_on_key(json_obj,"users.^",None,delete_func)
    assert obj == {
        "users": [
            {"id":7,"name":"paul"},
            {"id": 2, "name": "jon"}
        ],
        "map": {
            "a": 3,
            "x": 9
        }
    }


# todo - test error handling and seperate exit from error states
