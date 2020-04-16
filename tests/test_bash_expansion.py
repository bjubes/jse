import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from jse.bash import *
import pytest

def test_nested_object():
    #input:  [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}]
    corrupted_input = ['[score:32.5]', '[user:bob]', '[metadata:ip:192.168.1.102]', '[metadata:client:firefox]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [{'user':'bob',
                     'score': 32.5,
                     'metadata':{
                         'ip':'192.168.1.102',
                         'client':'firefox'
                     }}]

def test_same_keys_object_list():
    # 3x3
    #input: [{name:bob,id:1},{name:steve,id:3}, {name:ted,id:5}]
    corrupted_input = ['[name:bob,name:steve,name:ted]', '[name:bob,name:steve,id:5]', '[name:bob,name:steve,g:6]', '[name:bob,id:3,name:ted]', '[name:bob,id:3,id:5]', '[name:bob,id:3,g:6]', '[name:bob,g:4,name:ted]', '[name:bob,g:4,id:5]', '[name:bob,g:4,g:6]', '[id:1,name:steve,name:ted]', '[id:1,name:steve,id:5]', '[id:1,name:steve,g:6]', '[id:1,id:3,name:ted]', '[id:1,id:3,id:5]', '[id:1,id:3,g:6]', '[id:1,g:4,name:ted]', '[id:1,g:4,id:5]', '[id:1,g:4,g:6]', '[g:2,name:steve,name:ted]', '[g:2,name:steve,id:5]', '[g:2,name:steve,g:6]', '[g:2,id:3,name:ted]', '[g:2,id:3,id:5]', '[g:2,id:3,g:6]', '[g:2,g:4,name:ted]', '[g:2,g:4,id:5]', '[g:2,g:4,g:6]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {'name':'bob','id':1,'g':2},
        {'name':'steve','id':3, 'g':4},
        {'name':'ted','id':5, 'g':6}
    ]
    # 3x2
    #input: [{name:bob,id:1,x:3},{name:steve,id:3,x:5}]
    corrupted_input = ['[name:bob,name:steve]', '[name:bob,id:3]', '[name:bob,x:5]', '[id:1,name:steve]', '[id:1,id:3]', '[id:1,x:5]', '[x:3,name:steve]', '[x:3,id:3]', '[x:3,x:5]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {'name':'bob','id':1,'x':3},
        {'name':'steve','id':3, 'x':5},
    ]
    # 2x2
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

# failling currently
# 
# need to implement a consistent way to deal with
# any length list with objects with any number of parameters
#
# def test_unique_object_list():
#     # 2x2
#     #input:  [{a:1,b:2},{c:3,d:4}]
#     corrupted_input = ['[a:1,c:3]', '[a:1,d:4]', '[b:2,c:3]', '[b:2,d:4]']
#     value = fix_bash_brackets(corrupted_input)
#     assert value == [
#         {"a":1,"b":2},
#         {"b":3,"c":4}
#     ]


def test_simple_obj_list():
    # 3x1
    #input: [{a:1,b:2,c:3}]
    corrupted_input = ['[a:1]', '[b:2]', '[c:3]']
    value = fix_bash_brackets(corrupted_input)
    assert value == [
        {"a":1,"b":2,"c":3}
    ]

    # 1x3
    # does not get corrupted by bash, but is dual to 3x1
    inp = '[{a:1},{b:2},{c:3}]'
    value = parse_value(inp)
    assert value ==  [
        {"a":1},
        {"b":2},
        {"c":3}
    ]