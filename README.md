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
