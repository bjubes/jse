# jse (JSON editor)
[![Build Status](https://travis-ci.org/bjubes/jse.svg?branch=master)](https://travis-ci.org/bjubes/jse)
a quick and dirty command line JSON editor

##Usage
```
#jse <file> <mode> <key> <value>
jse config.json --edit app.version 0.3.3
jse todos.json --add todo.list {task:my_task,done:false}
jse problems.json --delete problems[99]
```
