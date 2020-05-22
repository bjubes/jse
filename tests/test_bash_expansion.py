import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from jse.bash import *
import pytest

def test_nested_object():
    #input:  [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}]
    corrupted_input = ['[score:32.5]', '[user:bob]', '[metadata:ip:192.168.1.102]', '[metadata:client:firefox]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [{'user':'bob',
                     'score': 32.5,
                     'metadata':{
                         'ip':'192.168.1.102',
                         'client':'firefox'
                     }}]

def test_nested_object_list():
    #input: [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}, {score:21.0,user:steve,metadata:{ip:192.168.1.147,client:chrome}}]
    corrupted_input = ['[score:32.5,', '[user:bob,', '[metadata:ip:192.168.1.102,', '[metadata:client:firefox,', 'score:21.0]', 'user:steve]', 'metadata:ip:192.168.1.147]', 'metadata:client:chrome]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [{'user':'bob',
                     'score': 32.5,
                     'metadata':{
                         'ip':'192.168.1.102',
                         'client':'firefox'
                     }},
                     {'user':'steve',
                     'score': 21.0,
                     'metadata':{
                         'ip':'192.168.1.147',
                         'client':'chrome'
                     }}]


def test_same_keys_object_list():
    # 3x3
    #input: [{name:bob,id:1},{name:steve,id:3}, {name:ted,id:5}]
    corrupted_input = ['[name:bob,name:steve,name:ted]', '[name:bob,name:steve,id:5]', '[name:bob,name:steve,g:6]', '[name:bob,id:3,name:ted]', '[name:bob,id:3,id:5]', '[name:bob,id:3,g:6]', '[name:bob,g:4,name:ted]', '[name:bob,g:4,id:5]', '[name:bob,g:4,g:6]', '[id:1,name:steve,name:ted]', '[id:1,name:steve,id:5]', '[id:1,name:steve,g:6]', '[id:1,id:3,name:ted]', '[id:1,id:3,id:5]', '[id:1,id:3,g:6]', '[id:1,g:4,name:ted]', '[id:1,g:4,id:5]', '[id:1,g:4,g:6]', '[g:2,name:steve,name:ted]', '[g:2,name:steve,id:5]', '[g:2,name:steve,g:6]', '[g:2,id:3,name:ted]', '[g:2,id:3,id:5]', '[g:2,id:3,g:6]', '[g:2,g:4,name:ted]', '[g:2,g:4,id:5]', '[g:2,g:4,g:6]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
        {'name':'bob','id':1,'g':2},
        {'name':'steve','id':3, 'g':4},
        {'name':'ted','id':5, 'g':6}
    ]
    # 3x2
    #input: [{name:bob,id:1,x:3},{name:steve,id:3,x:5}]
    corrupted_input = ['[name:bob,name:steve]', '[name:bob,id:3]', '[name:bob,x:5]', '[id:1,name:steve]', '[id:1,id:3]', '[id:1,x:5]', '[x:3,name:steve]', '[x:3,id:3]', '[x:3,x:5]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
        {'name':'bob','id':1,'x':3},
        {'name':'steve','id':3, 'x':5},
    ]
    # 2x2
    #input: [{name:bob,id:1},{name:steve,id:3}]
    corrupted_input = ['[name:bob,name:steve]', '[name:bob,id:3]', '[id:1,name:steve]', '[id:1,id:3]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
        {'name':'bob','id':1,},
        {'name':'steve','id':3}
    ]

    #input:  [{name:bob,id:1},{name:steve,id:3},{name:ted,id:5}]
    corrupted_input = ['[name:bob,name:steve,name:ted]', '[name:bob,name:steve,id:5]', '[name:bob,id:3,name:ted]', '[name:bob,id:3,id:5]', '[id:1,name:steve,name:ted]', '[id:1,name:steve,id:5]', '[id:1,id:3,name:ted]', '[id:1,id:3,id:5]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
        {'name':'bob','id':1,},
        {'name':'steve','id':3},
        {'name':'ted','id':5}
    ]

def test_unique_object_list_2x2():
    # 2x2
    #input:  [{a:1,b:2},{c:3,d:4}]
    corrupted_input = ['[a:1,c:3]', '[a:1,d:4]', '[b:2,c:3]', '[b:2,d:4]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
        {"a":1,"b":2},
        {"c":3,"d":4}
    ]

def test_simple_obj_list():
    # 3x1
    #input: [{a:1,b:2,c:3}]
    corrupted_input = ['[a:1]', '[b:2]', '[c:3]']
    value = parse_bash_brackets_value(corrupted_input)
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

def test_unique_object_list_3x2():
    #input: [{a:1,b:2,c:3},{d:4,e:5,f:6}]
    corrupted_input = ['[a:1,d:4]', '[a:1,e:5]', '[a:1,f:6]', '[b:2,d:4]', '[b:2,e:5]', '[b:2,f:6]', '[c:3,d:4]', '[c:3,e:5]', '[c:3,f:6]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
       {"a":1,"b":2,"c":3},
       {"d":4,"e":5,"f":6}
    ]


def test_unique_object_list_2x3():
    #input: [{a:1,b:2},{c:3,d:4},{e:5,f:6}]
    corrupted_input = ['[a:1,c:3,e:5]', '[a:1,c:3,f:6]', '[a:1,d:4,e:5]', '[a:1,d:4,f:6]', '[b:2,c:3,e:5]', '[b:2,c:3,f:6]', '[b:2,d:4,e:5]', '[b:2,d:4,f:6]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
       {"a":1,"b":2},
       {"c":3,"d":4},
       {"e":5,"f":6}
    ]

def test_unique_object_list_3x4():
    #input: [{a:1,b:2,c:3},{d:4,e:5,f:6},{g:7,h:8,i:9},{j:10,k:11,l:12}]
    corrupted_input = ['[a:1,d:4,g:7,j:10]', '[a:1,d:4,g:7,k:11]', '[a:1,d:4,g:7,l:12]', '[a:1,d:4,h:8,j:10]', '[a:1,d:4,h:8,k:11]', '[a:1,d:4,h:8,l:12]', '[a:1,d:4,i:9,j:10]', '[a:1,d:4,i:9,k:11]', '[a:1,d:4,i:9,l:12]', '[a:1,e:5,g:7,j:10]', '[a:1,e:5,g:7,k:11]', '[a:1,e:5,g:7,l:12]', '[a:1,e:5,h:8,j:10]', '[a:1,e:5,h:8,k:11]', '[a:1,e:5,h:8,l:12]', '[a:1,e:5,i:9,j:10]', '[a:1,e:5,i:9,k:11]', '[a:1,e:5,i:9,l:12]', '[a:1,f:6,g:7,j:10]', '[a:1,f:6,g:7,k:11]', '[a:1,f:6,g:7,l:12]', '[a:1,f:6,h:8,j:10]', '[a:1,f:6,h:8,k:11]', '[a:1,f:6,h:8,l:12]', '[a:1,f:6,i:9,j:10]', '[a:1,f:6,i:9,k:11]', '[a:1,f:6,i:9,l:12]', '[b:2,d:4,g:7,j:10]', '[b:2,d:4,g:7,k:11]', '[b:2,d:4,g:7,l:12]', '[b:2,d:4,h:8,j:10]', '[b:2,d:4,h:8,k:11]', '[b:2,d:4,h:8,l:12]', '[b:2,d:4,i:9,j:10]', '[b:2,d:4,i:9,k:11]', '[b:2,d:4,i:9,l:12]', '[b:2,e:5,g:7,j:10]', '[b:2,e:5,g:7,k:11]', '[b:2,e:5,g:7,l:12]', '[b:2,e:5,h:8,j:10]', '[b:2,e:5,h:8,k:11]', '[b:2,e:5,h:8,l:12]', '[b:2,e:5,i:9,j:10]', '[b:2,e:5,i:9,k:11]', '[b:2,e:5,i:9,l:12]', '[b:2,f:6,g:7,j:10]', '[b:2,f:6,g:7,k:11]', '[b:2,f:6,g:7,l:12]', '[b:2,f:6,h:8,j:10]', '[b:2,f:6,h:8,k:11]', '[b:2,f:6,h:8,l:12]', '[b:2,f:6,i:9,j:10]', '[b:2,f:6,i:9,k:11]', '[b:2,f:6,i:9,l:12]', '[c:3,d:4,g:7,j:10]', '[c:3,d:4,g:7,k:11]', '[c:3,d:4,g:7,l:12]', '[c:3,d:4,h:8,j:10]', '[c:3,d:4,h:8,k:11]', '[c:3,d:4,h:8,l:12]', '[c:3,d:4,i:9,j:10]', '[c:3,d:4,i:9,k:11]', '[c:3,d:4,i:9,l:12]', '[c:3,e:5,g:7,j:10]', '[c:3,e:5,g:7,k:11]', '[c:3,e:5,g:7,l:12]', '[c:3,e:5,h:8,j:10]', '[c:3,e:5,h:8,k:11]', '[c:3,e:5,h:8,l:12]', '[c:3,e:5,i:9,j:10]', '[c:3,e:5,i:9,k:11]', '[c:3,e:5,i:9,l:12]', '[c:3,f:6,g:7,j:10]', '[c:3,f:6,g:7,k:11]', '[c:3,f:6,g:7,l:12]', '[c:3,f:6,h:8,j:10]', '[c:3,f:6,h:8,k:11]', '[c:3,f:6,h:8,l:12]', '[c:3,f:6,i:9,j:10]', '[c:3,f:6,i:9,k:11]', '[c:3,f:6,i:9,l:12]']
    value = parse_bash_brackets_value(corrupted_input)
    assert value == [
        {"a":1,"b":2,"c":3},
        {"d":4,"e":5,"f":6},
        {"g":7,"h":8,"i":9},
        {"j":10,"k":11,"l":12}
    ]

def test_simple_object():
    #input: {a:1,b:2,c:3}
    corrupted_input = ['a:1', 'b:2', 'c:3']
    value = parse_value_from_bash(corrupted_input)
    assert value == {
        "a":1,"b":2,"c":3
    }