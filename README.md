# jse - JSON editor

quickly edit JSON files from the command line

[![Build Status](https://travis-ci.org/bjubes/jse.svg?branch=master)](https://travis-ci.org/bjubes/jse)

## Usage
```
$ jse <file> <mode> <key> <value>
```
### Examples
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
