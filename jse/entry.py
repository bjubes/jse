#!/usr/bin/env python3
import json
import sys
import click

from .editor import *
from .bash import *

VERSION = "0.1.1"

# AliasedGroup allows commands to be shortened, so 'd', 'del', and 'delete'
# can all be used for the delete sub command
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
@click.argument('file',type=click.Path(exists=True))
@click.pass_context
@click.version_option(version=VERSION)
def main(ctx,file):
    ctx.obj = file

@main.command(short_help='add a new element or append to a list')
@click.argument('query')
@click.argument('value', nargs=-1, required=True)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.option('-d','--debug', is_flag=True,help="get debugging information")
@click.pass_obj
def add(file,query,value,preview,debug):
    try:
        value = parse_value_from_bash(value)
        with open(file,'r+') as f:
            json_obj = json.load(f)         
            obj,key = query_object(json_obj,query)
            if key == None:
                # multiple returns
                for o,key in obj:
                    add_func(o,key,value)    
            else:
                add_func(obj,key,value)
            if preview:
                click.echo(json.dumps(json_obj,indent=4))
                return
            save_json(f,json_obj)
    except EditorError as err:
        handle_error(err,debug)


@main.command(short_help='change an existing key to a new value')
@click.argument('query')
@click.argument('value', nargs=-1, required=True)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.option('-d','--debug', is_flag=True,help="get debugging information")
@click.pass_obj
def edit(file,query,value,preview,debug):
    try:
        value = parse_value_from_bash(value)
        with open(file,'r+') as f:
            json_obj = json.load(f)         
            obj,key = query_object(json_obj,query)
            if key == None:
                # multiple returns
                for o,key in obj:
                    edit_func(o,key,value)    
            else:
                edit_func(obj,key,value)
            if preview:
                click.echo(json.dumps(json_obj,indent=4))
                return
            save_json(f,json_obj)
    except EditorError as err:
        handle_error(err,debug)


@main.command(short_help='delete an element')
@click.argument('query', nargs=-1)
@click.option('-p','--preview', is_flag=True,help="preview change without writing to file")
@click.option('-d','--debug', is_flag=True,help="get debugging information")
@click.pass_obj
def delete(file,query,preview,debug):
    try:
        with open(file,'r+') as f:
            json_obj = json.load(f)       
            for q in query:
                obj,key = query_object(json_obj,q)
                if key == None:
                    # multiple returns
                    for o,k in obj:
                        delete_func(o,k)    
                else:
                    delete_func(obj,key)
            if preview:
                click.echo(json.dumps(json_obj,indent=4))
                return
            save_json(f,json_obj)
    except EditorError as err:
       handle_error(err,debug)

def save_json(f, json_obj):
        f.seek(0)
        f.truncate()
        json.dump(json_obj,f,indent=4)

def print_err(err):
    click.echo(click.style(str(err),fg='bright_red'),file=sys.stderr)

def handle_error(err,debug):
    print_err(err)
    if debug:
        print_err("\nDebug enabled. Stack Trace:")
        raise err


if __name__ == '__main__':
    main()
