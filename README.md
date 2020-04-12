# jse - JSON editor [![Build Status](https://travis-ci.org/bjubes/jse.svg?branch=master)](https://travis-ci.org/bjubes/jse)


quickly edit JSON files from the command line


## Usage
```
$ jse <file> <mode> <key> <value>
```
### Quick Use
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
we can also use dot notation interchagably
```
$ jse example.json -d users.0
```
result:
```
# example.json
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": false}
    ]
}
```
now lets make charlie an admin. To edit an existing field we use the edit command with -e or --edit. Edit gets both a key and a value to change that key to.
```
$ jse example.json -e users.1.admin true
```
result:
```
# example.json
{
    "users": [
        {"name": "bob", "age": 57, "admin": true},
        {"name": "charlie", "age": 37, "admin": true}
    ]
}
```
jse is smart enough to infer datatypes from the command line. it can also accept nested,complex objects and arrays. We can see this by adding a new object to the file
```
$ jse example.json -a highscore [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}},{}]
```