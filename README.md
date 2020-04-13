# jse - JSON editor [![Build Status](https://travis-ci.org/bjubes/jse.svg?branch=master)](https://travis-ci.org/bjubes/jse)


quickly edit JSON files from the command line


## Usage
```
$ jse <file> <mode> <key> <value>
```
### TLDR Usage
edit an existing key: ``` -e --edit```
```
$ jse config.json --edit app.version 0.3.3
```
add a new element: ``` -a --add```
```
$ jse todo.json --add list.shopping {task:eggs,done:false}
```
delete a value: ``` -d --delete```
```
$ jse problems.json --delete problems[99]
```
There are more [examples with JSON files below](#examples)

### Installing

comming soon - pip install :)

#### Running from Source
requiremets:
- python 3

1. clone the repository
2. make it executable `chmod +x jse.py`
3. put in on the path `ln -s /path/to/jse.py ~/.local/bin/jse`

jse requires no pip packages to run, but does use pytest for tests.


### Examples
```
# example.json
{
    "users": [
        {"name": "alice", "age": 21, "admin": false},
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": false}
    ]
}
```

Lets delete the user alice using jse. All we need is the path to her `user` object
```
$ jse example.json -d users[0]
```
we can use both index or dot notation
```
$ jse example.json -d users.0
```
```
# example.json
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": false}
    ]
}
```
now lets make charlie an admin. To edit an existing field we use the edit command with -e or --edit. Edit takes a key to change and its new value.
```
$ jse example.json -e users.1.admin true
```
```
# example.json
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": true}
    ]
}
```
jse is smart enough to infer datatypes from the command line. it can also accept complex nested objects and arrays in a terse, quote-free format. Lets add a new nested field to the file
```
$ jse example.json -a highscore [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}]
```
```
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": true}
    ],
    "highscore": [
        {
            "score": "32.5",
            "user": "bob",
            "metadata": {
                "ip": "192.168.1.102",
                "client": "firefox"
            }
        }
    ]
}
```
jse also understands lists, so we can use -a to add new elements to a list without needing an explicit index
```
$ jse example.json -a highscore {"score":52,"user": "charlie"}
```
```
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": true}
    ],
    "highscore": [
        {
            "score": "32.5",
            "user": "bob",
            "metadata": {
                "ip": "192.168.1.102",
                "client": "firefox"
            }
        },
        {
            "score": 52.0,
            "user": "charlie"
        }
    ]
}
```
error messages are also meant to be informative, because no one wants a KeyError
```
$ jse example.json -a users.0.name "not bob"
'name' already has a value. Use --edit to modify it
```
```
$ jse example.json -d users[2]
There is no element with index 2. The largest index is 1
```

You can also delete mulitple keys using -d, by passing them seperately
```
$ jse example.json -d users.0.age users.1.age
```
```
{
    "users": [
        {
            "name": "bob",
            "admin": true,
        },
        {
            "name": "charlie",
            "admin": true
        }
    ]
    ...
}
```
