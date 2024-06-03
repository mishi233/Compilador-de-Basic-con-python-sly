# bascontext.py
#
# Clase de alto nivel que contiene todo lo relacionado con el análisis/ejecución de un 
# programa en Basic.  Sirve como depósito de información sobre el programa, incluido el 
# código fuente, informes de errores, etc.
from rich      import print
import time

from baslex    import Lexer
from basparse  import Parser
from basinterp import Interpreter
from basircode import CodeTranslator
from basast    import *
from basrender import DotRender
from basrich import print_ast_tree

class Context:
  def __init__(self, config):
    self.lexer  = Lexer()
    self.parser = Parser()
    self.interp = Interpreter(self, config)
    self.translator = CodeTranslator()
    self.source = ''
    self.ast = DotRender()
    self.rich = print_ast_tree
    self.have_errors = False
    self.config = config

  def parse(self, source):
    self.have_errors = False
    self.source = source
    self.ast = self.parser.parse(self.lexer.tokenize(self.source))
  
  def run(self):
    if not self.have_errors:
      if self.config['estadisticas'] or self.config['escribir_estadisticas']:
        start_time = time.time() 
        result =  self.interp.interpret(self.ast, self.config)
        end_time = time.time() 
        if self.config['estadisticas']:
          print("El tiempo de ejecución a sido de  " , end_time - start_time, "s")
        elif self.config['escribir_estadisticas']:
          with open('instrucciones_ejecutadas.txt', 'a') as f:
            f.write("El tiempo de ejecución ha sido de " + str(end_time - start_time) + "s\n")
      else:
        result =  self.interp.interpret(self.ast, self.config)

      return result

  def find_source(self, node):
    indices = self.parser.index_position(node)
    if indices:
      return self.source[indices[0]:indices[1]]
    else:
      return f'{type(node).__name__} (ñ unavailable)'

  def error(self, position, message):
    if isinstance(position, Node):
      lineno = self.parser.line_position(position)
      (start, end) = (part_start, part_end) = self.parser.index_position(position)
      while start >= 0 and self.source[start] != '\n':
        start -=1

      start += 1
      while end < len(self.source) and self.source[end] != '\n':
        end += 1
      print()
      print(self.source[start:end])
      print(" "*(part_start - start), end='')
      print("^"*(part_end - part_start))
      print(f'{lineno}: {message}')

    else:
      print(f'{position}: {message}')
    self.have_errors = True
  
  def print_tokens(self, source):
    print(self.lexer.pprint(source))

  def print_ast(self, source, args):
    top = self.parser.parse(self.lexer.tokenize(source))
    if args.style == "dot":
      print(self.ast.render(top))
    else:
      print(self.rich(top))

  def generate_code(self):
    if not self.have_errors:
      result =  self.translator.intermedium_code(self.ast)
      return result