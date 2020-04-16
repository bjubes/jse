#!/usr/bin/env python3
import json
import sys
import click

from .editor import *
from .bash import *

VERSION = "0.0.6"

class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: {}'.format(', '.join(sorted(matches))))

@click.group(cls=AliasedGroup)
@click.argument('file')
@click.pass_context
@click.version_option(version=VERSION)
def main(ctx,file):
    ctx.obj = file

@main.command(short_help='add a new element or append to a list')
@click.argument('query')
@click.argument('value', nargs=-1)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.pass_obj
def add(file,query,value,preview):
    value = parse_value_from_bash(value)
    json = load_json(file)
    obj,key = query_object(json,query)
    add_func(obj,key,value)
    if preview:
        print(json)
        return
    save_json(file,json) 

@main.command(short_help='change an existing key to a new value')
@click.argument('query')
@click.argument('value', nargs=-1)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.pass_obj
def edit(file,query,value,preview):
    value = parse_value_from_bash(value)
    json = load_json(file)
    obj,key = query_object(json,query)
    edit_func(obj,key,value)
    if preview:
        print(json)
        return
    save_json(file,json) 

@main.command(short_help='delete an element')
@click.argument('query', nargs=-1)
@click.pass_obj
def delete(file,query):
    json = load_json(file)
    for q in query:
        obj,key = query_object(json,q)
        delete_func(obj,key)
    save_json(file,json) 

def load_json(filename):
    with open(filename) as f:
        json_dict = json.load(f)
        return json_dict
          
def save_json(filename, json_obj):
    with open(filename,'w') as f:
        json.dump(json_obj,f,indent=4)


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


if __name__ == '__main__':
    jse()