# basic.py
'''
usage: basic.py [-h] [-a style] [-o OUT] [-l] [-D] [-p] [-I] [--sym] [-S] [-R] input

Compiler for BASIC DARTMOUTH 64

positional arguments:
  input              BASIC program file to compile

optional arguments:
  -h, --help         show this help message and exit
  -D, --debug        Generate assembly with extra information (for debugging purposes)
  -o OUT, --out OUT  File name to store generated executable
  -l, --lex          Store output of lexer
  -a STYLE           Generate AST graph as DOT format
  -I, --ir           Dump the generated Intermediate representation
  --sym              Dump the symbol table
  -S, --asm          Store the generated assembly file
  -R, --exec         Execute the generated program
'''
from contextlib import redirect_stdout
from rich       import print
from bascontext import Context

import argparse


def parse_args():
  cli = argparse.ArgumentParser(
    prog='basic.py',
    description='Compiler for BASIC programs'
  )

  cli.add_argument(
    '-v', '--version',
    action='version',
    version='0.4')

  fgroup = cli.add_argument_group('Formatting options')

  fgroup.add_argument(
    'input',
    type=str,
    nargs='?',
    help='BASIC program file to compile')

  mutex = fgroup.add_mutually_exclusive_group()

  mutex.add_argument(
    '-l', '--lex',
    action='store_true',
    default=False,
    help='Store output of lexer')

  mutex.add_argument(
    '-a', '--ast',
    action='store',
    dest='style',
    choices=['dot', 'txt'],
    help='Generate AST graph as DOT format')

  mutex.add_argument(
    '--sym',
    action='store_true',
    help='Dump the symbol table')

  return cli.parse_args()


if __name__ == '__main__':

  args = parse_args()
  context = Context()

  if args.input: fname = args.input
  
  with open(fname, encoding='utf-8') as file:
    source = file.read()

  if args.lex:
    flex = fname.split('.')[0] + '.lex'
    print(f'print lexer: {flex}')
    with open(flex, 'w', encoding='utf-8') as fout:
      with redirect_stdout(fout):
        context.print_tokens(source)

  elif args.style:
    base = fname.split('.')[0]

    fast = base + '.' + args.style
    print(f'print ast: {fast}')
    with open(fast, 'w') as fout:
      with redirect_stdout(fout):
        context.print_ast(source, args.style)
    
  else:

    context.parse(source)
    context.run()
