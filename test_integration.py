from jse import *
import pytest

def test_basic_edit():
    json_obj = {'a':'b'}
    query = 'a'
    value = 'x'
    func = edit_func
    create_keys = False
    
    obj = operate_on_key(json_obj,query,value,func)
    assert obj == {'a':'x'}

def test_basic_add():
    json_obj = {'a':'b'}
    query = 'c'
    value = 'x'
    func = add_func
    create_keys = True
    
    obj = operate_on_key(json_obj,query,value,func)
    assert obj == {'a':'b','c':'x'}

def test_list_add_auto_index():
    listname = "mylist"
    json_obj = {listname:[]}
    value = 'x'
    func = add_func
    create_keys = True
    obj = operate_on_key(json_obj,listname,value,func)
    assert obj == {listname:[value]}


def test_list_add_manual_index():
    listname = "mylist"
    json_obj = {listname:[]}
    query = listname + ".0"
    value = 'x'
    func = add_func
    create_keys = True
    obj = operate_on_key(json_obj,query,value,func)
    assert obj == {listname:[value]}

def test_obj_add():
    json_obj = {
        "my_obj": {}
    }
    query = "my_obj.name"
    value = "waldo"
    func = add_func
    create_keys = True
    obj = operate_on_key(json_obj,query,value,func)
    assert obj == {
        "my_obj" : {
            "name":"waldo"
        }
    }
