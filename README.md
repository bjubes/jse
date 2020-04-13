# jse - JSON Editor [![Build Status](https://travis-ci.org/bjubes/jse.svg?branch=master)](https://travis-ci.org/bjubes/jse)


quickly edit json files from the command line

jse is pragmatic and terse. It lets you edit json fast, without needing to care about quotes, types, exact indexes, or any of the stuff that makes json a pain.
## Usage
```
$ jse <file> <mode> <key> <value>
```
#### TLDR Version
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
full [examples with json files](#examples) below

## Installing

comming soon - pip install :)

### Running from Source
requiremets:
- python 3

steps:

1. clone the repository
2. make it executable `chmod +x jse.py`
3. put in on the path `ln -s /path/to/jse.py ~/.local/bin/jse`

jse has no package dependencies (it literally just edits json), but does use pytest for tests.


## Examples
lets start with a json file
```json
# example.json
{
    "users": [
        {"name": "alice", "age": 21, "admin": false},
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": false}
    ]
}
```

We want to delete the user alice using jse. All we need to do is specify `-d` or `--delete` mode and the path to her `user` object
```
$ jse example.json -d users[0]
```
we can use both index or dot notation
```
$ jse example.json -d users.0
```
```json
# example.json
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": false}
    ]
}
```
now lets make charlie an admin. To edit an existing field we use the edit command with `-e` or `--edit`. Edit takes a key to change and its new value.
```
$ jse example.json -e users.1.admin true
```
```json
# example.json
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": true}
    ]
}
```
jse is smart enough to infer datatypes from the command line. it can also accept complex nested objects and arrays in a terse, quote-free format. Lets add a new nested field to the file with `--add` or `-a`
```
$ jse example.json -a highscore [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}]
```
```json
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
jse also understands lists, so we can add new elements to a one without needing an explicit index. It will infer we are trying to append from `--add` instead of changing the list to an object (`--edit`)
```
$ jse example.json -a highscore {"score":52,"user": "charlie"}
```
```json
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
```json
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
