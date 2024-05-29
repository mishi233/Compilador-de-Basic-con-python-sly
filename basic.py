import random

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
  -v, --version: Imprimir la versión
  -A, --array-base: el índice mínimo de los arreglos, normalmente en 1
  -n, --no-run: No ejecuta el programa después de analizarlo.
  -g, --go-next: Si no existe una ramificación, vaya a la siguiente línea
  -t, --trace: activa el seguimiento al número de líneas
  --tabs: fija el número de espacios para separación de elementos por coma
  -p, --print-stats: cuando el programa finaliza, imprimir estadisticas.
  -w, --write-stats: a la finalización, escriba las estadísticas a un archivo
  -o, --output-file: redirecciona el PRINT al nombre del archivo
  -i, --input-file: redirecciona INPUT al nombre de archivo.
  -r, --random: la semilla del generador de números aleatorios
  -s, --slicing: Activa el corte de cadena (apaga los arreglos de cadena)
  -u, --uper-case: Convertir todas las entradas a mayúsculas
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
  
  mutex.add_argument(
    '-u', '--uppercase',
    action='store_true',
    help='Convertir todas las entradas a mayúsculas')

  mutex.add_argument(
      '-A', '--array-base',
      action='store_true',
      help='El índice mínimo de los arreglos, normalmente en 1'
  )

  mutex.add_argument(
      '-n', '--no-run',
      action='store_true',
      help='No ejecuta el programa después de analizarlo'
  )

  mutex.add_argument(
      '-g', '--go-next',
      action='store_true',
      help=' Si no existe una ramificación, vaya a la siguiente línea'
  )

  mutex.add_argument(
      '-t', '--trace',
      action='store_true',
      help=' activa el seguimiento al número de líneas'
  )
  
  mutex.add_argument(
        '--tabs',
        action='store',
        type=int,
        dest='numero_espacios',
        help='Fija el número de espacios para separación de elementos por coma'
    )
  
  mutex.add_argument(
      '-p', '--print-stats',
      action='store_true',
      help='cuando el programa finaliza, imprimir estadisticas'
  )

  mutex.add_argument(
      '-w', '--write-stats',
      action='store_true',
      help='a la finalización, escriba las estadísticas a un archivos'
  )

  mutex.add_argument(
      '-o', '--output-file',
      action='store_true',
      help=' redirecciona el PRINT al nombre del archivo'
  )

  mutex.add_argument(
      '-i', '--input-file',
      action='store',
      type=str,
      dest='archivo_origen',
      help='redirecciona INPUT al nombre de archivo'
  )
  mutex.add_argument(
        '-r','--random',
        action='store',
        type=int,
        dest='random_seed',
        help='la semilla del generador de números aleatorios'
    )
  
  mutex.add_argument(
      '-s', '--slicing',
      action='store_true',
      help='Activa el corte de cadena (apaga los arreglos de cadena)'
  )

  mutex.add_argument(
      '-T', '--translate',
      action='store_true',
      help='Genera código Intermedio'
  )
  return cli.parse_args()


if __name__ == '__main__':

  args = parse_args()

  config = {
    'indice': args.array_base if args.array_base else False,
    'goNext': args.go_next if args.go_next else False,
    'seguimientoPorLinea': args.trace if args.trace else False,
    'numeroEspacios': args.numero_espacios if args.numero_espacios else 0,
    'estadisticas': args.print_stats if args.print_stats else False,
    'escribir_estadisticas': args.write_stats if args.write_stats else False,
    'escribir_print': args.output_file if args.output_file else False,
    'leer_archivo': args.archivo_origen if args.archivo_origen else False,
    'semilla_random': args.random_seed if args.random_seed else random.random(),
    'corteDeCadena': args.slicing if args.slicing else False
  }

  context = Context(config)

  if args.input: fname = args.input
  
  with open(fname, encoding='utf-8') as file:
    source = file.read()

  if args.uppercase:
    source = source.upper()

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
        context.print_ast(source, args)
  
  elif args.translate:
    context.parse(source)
    context.generate_code()

  else:
    context.parse(source)
    if not args.no_run:
      context.run()