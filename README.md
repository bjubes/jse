# jse - JSON Editor [![build status](https://github.com/bjubes/jse/actions/workflows/test.yml/badge.svg)](https://github.com/bjubes/jse/actions/workflows/test.yml) [![codecov](https://codecov.io/gh/bjubes/jse/branch/master/graph/badge.svg)](https://codecov.io/gh/bjubes/jse)

quickly edit json files from the command line

jse is pragmatic and terse. It lets you edit json fast, without needing to care about quotes, types, exact indexes, or any of the stuff that makes json a pain.

## Usage

```
$ jse FILE COMMAND QUERY VALUE
```

#### TLDR Version

edit an existing key: `e` or `edit`

```
$ jse config.json edit app.version 0.3.3
```

add a new element: `a` or `add`

```
$ jse todo.json add list.shopping {task:eggs,done:false}
```

delete a value: `d` or `delete`

```
$ jse problems.json delete problems[99]
```

full [examples with json files](#examples) below

## Installing

```
pip3 install jse
```

### Running from Source

Requirements:

- Python 3.7+
- [Click](https://pypi.org/project/click/)

Steps:

1. clone the repository
2. install click `pip3 install click`
3. make the run script executable `chmod +x run.py`
4. place jse on the path `ln -s /path/to/run.py ~/.local/bin/jse`

Using poetry is recommended if you plan to contribute

```bash
$ pip3 install poetry
$ poetry install
$ poetry shell
```

## Examples

Assume this json file is in the current directory

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

To delete the user alice using jse, all we need to do is specify `d` or `delete` mode and the path to her `user` object

```
$ jse example.json d users[0]
```

We can use both index or dot notation.

```shell
$ jse example.json d users.0   #users.first or users.^ also work
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

Now lets make charlie an admin. To edit an existing field, use the edit command with `e` or `edit`. Edit takes a key to change and its new value.

```
$ jse example.json e users.1.admin true
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

jse is smart enough to infer datatypes from the command line. it can also accept complex nested objects and arrays in a terse, quote-free format. Lets add a new nested field to the file with `add` or `a`

```
$ jse example.json a highscore [{score:32.5,user:bob,metadata:{ip:192.168.1.102,client:firefox}}]
```

```json
{
  "users": [
    { "name": "bob", "age": 57, "admin": true },
    { "name": "charlie", "age": 37, "admin": true }
  ],
  "highscore": [
    {
      "score": 32.5,
      "user": "bob",
      "metadata": {
        "ip": "192.168.1.102",
        "client": "firefox"
      }
    }
  ]
}
```

jse also understands lists, so you can add new elements to one without needing an explicit index. It will infer we are trying to append from `add` instead of changing the list itself to an object (`edit`)

```
$ jse example.json a highscore {score:52,user:charlie}
```

```json
{
  "users": [
    { "name": "bob", "age": 57, "admin": true },
    { "name": "charlie", "age": 37, "admin": true }
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

first and last (or `^` and `$`) can also be used as a list index for any operation

```
$ jse example.json a users.first {name:jon,age:22,admin:false}
```

```json
{
  "users": [
    { "name": "jon", "age": 22, "admin": false },
    { "name": "bob", "age": 57, "admin": true },
    { "name": "charlie", "age": 37, "admin": true }
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

jse's error messages are informative, because no one wants a generic KeyError

```
$ jse example.json a users.0.name "not bob"
'name' already has a value. Use the edit command to modify it
```

```
$ jse example.json d users[2]
There is no element with index 2. The largest index is 1
```

You can also delete mulitple keys in one command
``
$ jse example.json d users.0.age users.1.age users.2.age

````
```json
{
    "users": [
        {
            "name": "jon",
            "admin": false,
        },
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
````

No need to specify every element, just use the `*` or `all` operator

```shell
$ jse example.json d users.*.age # or users.all.age
```
