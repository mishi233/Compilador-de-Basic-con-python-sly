# This file provides the runtime support for running a basic program
# Assumes the program has been parsed using basparse.py

import sys
import math
import random

from typing import Dict, Union

from basast import *

class BasicExit(BaseException):
  pass

class BasicContinue(Exception):
  pass


def _is_truthy(value):
  if value is None:
    return False
  elif isinstance(value, bool):
    return value
  else:
    return True


class Interpreter(Visitor):
  # Inicializa el interprete. prog es un Node
  # que contiene mapeo (line,statement)
  def __init__(self, prog, config, verbose=False):
    self.prog    = prog
    
    self.verbose = verbose

    self.indice = 0
    if config['indice']:
      self.indice = 1

    self.goNext = config['goNext']
    self.segLinea = config['seguimientoPorLinea']
    self.numeroEspacios = config['numeroEspacios']
    self.printEnArchivo = config['escribir_print']

    if self.numeroEspacios < 0:
      print("NO SE PUEDE TENER UN ESPACIADO NEGATIVO")
      BasicExit()


    self.functions = {           # Built-in function table
      'SIN': lambda x: math.sin(x),
      'COS': lambda x: math.cos(x),
      'TAN': lambda x: math.tan(x),
      'ATN': lambda x: math.atan(x),
      'EXP': lambda x: math.exp(x),
      'ABS': lambda x: abs(x),
      'LOG': lambda x: math.log(x),
      'SQR': lambda x: math.sqrt(x),
      'INT': lambda x: int(x),
      'RND': lambda x: random.random(),
      'TAB': lambda x: ' '*x
    }

  @classmethod
  def interpret(cls, prog:Dict[int, Statement], config, verbose=False):
    basic = cls(prog, config, verbose)
    try:
        basic.run(config)
    except BasicExit:
      pass

  def error(self, message):
    sys.stderr.write(message)
    raise BasicExit()

  def _check_numeric_operands(self, instr, left, right):
    if isinstance(left, Union[int,float]) and isinstance(right, Union[int,float]):
      return True
    else:
      self.error(f"{instr.op} OPERANDS MUST BE NUMBERS")

  def _check_numeric_operand(self, instr, value):
    if isinstance(value, Union[int,float]):
      return True
    else:
      self.error(f"{instr.op} operand must be a number")

  # print methods (view: Norvig)
  def print_string(self, s) -> None:
    '''
    Print a string, keeping track of column, 
    and advancing to newline if at or beyond
    column 80.
    '''
    if self.printEnArchivo:
      with open('output_file.txt', 'a') as f:
          if self.column + len(s) >= 80:
              f.write('\n')  # Agrega un salto de línea si se supera el límite de la columna
              self.column = 0  # Reinicia la columna a 0
          f.write(s)
          f.write('\n')
    else:
      print(s, end='')
      self.column += len(s)
      if self.column >= 80:
        self.newline()
  
  def pad(self, width) -> None:
    '''
    Pad out to the column that is the next
    multiple of width
    '''
    while self.column % width != 0:
      self.print_string(' ')
  
  def newline(self):
    print(); self.column = 0

  # Collect all data statements
  def collect_data(self):
    self.data = []
    aux = []
    for lineno in self.stat:
      if isinstance(self.prog[self.stat[lineno][0]][self.stat[lineno][1]], Data):
        aux += self.prog[self.stat[lineno][0]][self.stat[lineno][1]].plist

        for i, data in enumerate(aux):
            if isinstance(data, Unary):
                aux[i] = Number(int(data.expr.value) * -1)

        self.data = aux

    self.dc = 0                  # Initialize the data counter

  # Check for end statements
  def check_end(self):
    has_end = False
    for lineno in self.stat:
      if isinstance(self.prog[self.stat[lineno][0]][self.stat[lineno][1]], End) and not has_end:
        has_end = lineno
    if not has_end:
      self.error("NO END INSTRUCTION")
    elif has_end != lineno:
      self.error("END IS NOT LAST")

  # Check loops
  def check_loops(self):
    for pc in range(len(self.stat)):
      lineno = self.stat[pc]
      if isinstance(self.prog[lineno[0]][lineno[1]], For):
        loopvar = self.prog[lineno[0]][lineno[1]].ident
        for i in range(pc + 1, len(self.stat)):
          if isinstance(self.prog[self.stat[i][0]][self.stat[i][1]], Next):
            nextvar = self.prog[self.stat[i][0]][self.stat[i][1]].var
            if nextvar != loopvar:
              continue
            self.loopend[pc] = i
            break
        else:
          self.error(f"FOR WITHOUT NEXT AT LINE {self.stat[pc][0]}")

  def goNextCorrections(self):
    encontrado = 0
    for lineno in self.stat:
      if isinstance(self.prog[self.stat[lineno][0]][self.stat[lineno][1]], Goto):
        lineaDestino = self.prog[self.stat[lineno][0]][self.stat[lineno][1]].num.value
        for line in self.prog.keys():
          if lineaDestino == line:
            encontrado = 1
        
        if encontrado == 0:
          for line in self.prog.keys():
            if int(line) > int(lineaDestino):
              self.prog[self.stat[lineno][0]][self.stat[lineno][1]].num.value = line
              break
        else:
          print("LA DIRECCIÓN PARA EL GOTO ESTÁ FUERA DE LOS LÍMITES")
          raise BasicExit()

        encontrado = 0


    


  # Change the current line number
  def goto(self, lineno):
    if not any('90' in value for value in self.stat.values()):
      self.error(f"UNDEFINED LINE NUMBER {lineno.value} AT LINE {self.stat[self.pc][0]}")

    for clave, valor in self.stat.items():
      if valor[0] == lineno.value:
        self.pc = clave

  # Run it
  def run(self, config):
    self.vars   = {}       # All variables
    self.lists  = {}       # List variables
    self.tables = {}       # Tables
    self.loops  = []       # Currently active loops
    self.loopend = {}      # Mapping saying where loops end
    self.gosub  = None     # Gosub return point (if any)
    self.column = 0        # Print column control
    stats_number_of_instructiones_executed = 0
    #Definición del diccionario de instrucciones y de lineas
    self.stat, self.prog = self.diccionarioDeInstrucciones(self.prog)
    self.pc = 0                  # Current program counter

    # Processing prior to running

    self.collect_data()          # Collect all of the data statements
    self.check_end()
    self.check_loops()
    if self.goNext:
      self.goNextCorrections()
    try:
      while True:
        line  = self.stat[self.pc][0]
        index  = self.stat[self.pc][1]
        instr = self.prog[line][index]

        #print(instr, end="\n")
        #print(self.vars, end="\n\n")
        #print(self.lists, end="\n\n")

        if self.segLinea:
          print(self.stat[self.pc][0])

        try:
          
          if self.verbose:
            print(line, instr.__class__.__name__)
          instr.accept(self)
          

        except BasicContinue as e:
          continue
          
        self.pc += 1
        stats_number_of_instructiones_executed += 1
    finally:
        if config['estadisticas']:
          print("Número de instrucciones ejecutadas:", stats_number_of_instructiones_executed)
        if config['escribir_estadisticas']:
            with open('instrucciones_ejecutadas.txt', 'a') as f:
                f.write("Número de instrucciones ejecutadas:" + str(stats_number_of_instructiones_executed)+ "\n")


  def diccionarioDeInstrucciones(self, prog):
    statementDict = {}
    lineDict = {}
    last_statement_line = "0"
    indice = 0
    pc = -1

    statements = prog.statements

    for statement in statements:
        statement_line = statement.line
        pc += 1

        if statement_line not in statementDict and statement_line != 0:
            statementDict[statement_line] = {} 

        #Tiene en cuenta que pueden haber varios stmt en una linea, por lo que los separa por indices
        if statement_line == 0:
            statement_line = last_statement_line
            indice += 1
            
        else:
            last_statement_line = statement_line
            indice = 0

        statement_value = statement.stmt
        statementDict[statement_line][indice] = statement_value
        lineDict[pc] = [statement_line, indice]

    return lineDict, statementDict


  # Assignment
  def assign(self, target, value):
    if isinstance(target, Array):
      var = target.var
      dim1 = target.dim1
      dim2 = target.dim2
    else:
      var = target
      dim1 = None
      dim2 = None

    lineno = self.stat[self.pc]

    if not dim1 and not dim2:
      if isinstance(value, Number):
        self.vars[var] = value.value
      else:
        self.vars[var] = value
    elif dim1 and not dim2:
      # List assignment
      x = int(dim1)
      if not var in self.lists:
        self.lists[var] = [0] * 10

      if x > len(self.lists[var]):
        self.error(f"DIMENSION TOO LARGE AT LINE {lineno}")
      self.lists[var][x-self.indice] = value
    
    elif dim1 and dim2:
      x = dim1.accept(self)
      y = dim2.accept(self)
      if not var in self.tables:
        temp = [0] * 10
        v = []
        for i in range(10):
          v.append(temp[:])
        self.tables[var] = v
      # Variable already exists
      if x > len(self.tables[var]) or y > len(self.tables[var][0]):
        self.error("DIMENSION TOO LARGE AT LINE {lineno}")
      self.tables[var][x - 1][y - 1] = value.accept(self)
  

  # --- Statement

  def visit_Remark(self, instr:Remark):
    pass

  def visit_Let(self, instr:Let):
    var   = instr.var
    value = instr.expr

    if not isinstance(value, int):
      value = value.accept(self)
    self.assign(var, value)

  def visit_Read(self, instr:Read):
    for target in instr.exprList:
      if self.dc >= len(self.data):
        # No more data.  Program ends
        print("NO EXISTE MÁS DATA, INTERRUMPCIÓN DEL PROGRAMA")
        raise BasicExit()
      value = self.data[self.dc]
      self.assign(target[0], value)
      self.dc += 1

  def visit_Data(self, instr:Data):
    pass

  # TODO: variable type
  def visit_Input(self, instr:Input): 

    for variable in instr.vlist:
      sys.stdout.write(variable)
      sys.stdout.write(":")
      value = input()
      try:
        value = Number(int(value))
      except ValueError:
        value = Number(float(value))
      self.assign(variable, value)
      
  # TODO: %.8g for numeric data. etc
  def visit_Print(self, instr:Print):
    items = instr.plist
    for pitem in items:
      if not pitem: continue
      if isinstance(pitem, Node):
        pitem = pitem.accept(self)
        
      if pitem == ',':   self.pad(15)
      elif pitem == ';': self.pad(3)
      elif isinstance(pitem, str):
        self.print_string(pitem)
      else:
        self.print_string(f'{pitem:g}')
      
      print(" " * self.numeroEspacios, end="")
    if (not items) or items[-1] not in (',', ';'):
      self.newline()
    
  def visit_Goto(self, instr:Goto):
    newline = instr.num
    self.goto(newline)
    raise BasicContinue()

  def visit_If(self, instr:If):
    relexpr = instr.expr
    newline = instr.jumpTo
    if _is_truthy(relexpr.accept(self)):
      self.goto(newline)
      raise BasicContinue()

  def visit_For(self, instr:For):
    loopvar = instr.ident.ident
    initval = instr.expr0
    finval  = int(instr.expr1.accept(self))
    stepval = instr.optstep

    # Check to see if this is a new loop
    if not self.loops or self.loops[-1][0] != self.pc:
      # Looks like a new loop. Make the initial assignment
      newvalue = initval
      self.assign(loopvar, initval)
      if not stepval:
        stepval = Number(1)
      else:
        stepval = stepval.accept(self)    # Evaluate step here
      self.loops.append((self.pc, stepval.value))
    else:
      # It's a repeat of the previous loop
      # Update the value of the loop variable according to the
      # step
      stepval = Number(self.loops[-1][1]).value

      newvalue = Binary('+', loopvar, stepval).accept(self)
    
      relop = '>=' if self.loops[-1][1] < 0 else '<='
      if (not _is_truthy(Logical(relop, newvalue, finval).accept(self))):
        # Loop is done. Jump to the NEXT
        self.pc = self.loopend[self.pc]
        self.loops.pop()
      else:
        self.assign(loopvar, newvalue)
          
  def visit_Next(self, instr:Next):
    lineno = self.stat[self.pc][0]
    if not self.loops:
      print(f"NEXT WITHOUT FOR AT LINE {lineno}")
      return
    nextvar = instr.var
    self.pc = self.loops[-1][0]
    loopinst = self.prog[self.stat[self.pc][0]][self.stat[self.pc][1]]
    forvar = loopinst.ident
    if nextvar != forvar:
      print(f"NEXT DOESN'T MATCH FOR AT LINE {lineno}")
      return
    raise BasicContinue()

  def visit_End(self, instr:End):
    raise BasicExit()
  
  def visit_Stop(self, instr:Stop):
    raise BasicExit()

  def visit_DefFunction(self, instr:DefFunction):
    fname = instr.name
    pname = instr.arguments
    expr  = instr.expresion

    def eval_func(pvalue, name=pname, self=self, expr=expr):
      self.assign(pname, pvalue)
      return expr.accept(self)
    self.functions[fname] = eval_func

  def visit_GoSub(self, instr:GoSub):
    newline = instr.line
    lineno  = self.stat[self.pc]
    if self.gosub:
      print(f"ALREADY IN A SUBROUTINE AT LINE {lineno}")
      return
    self.gosub = self.stat[self.pc]
    self.goto(newline)
    raise BasicContinue()

  def visit_Return(self, instr:Return):
    lineno = self.stat[self.pc]
    if not self.gosub:
      print(f"RETURN WITHOUT A GOSUB AT LINE {lineno}")
      return
    self.goto(self.gosub)
    self.gosub = None

  def visit_Dim(self, instr:Dim):
    for array in instr.dim:
      var = array.var
      dim1 = array.dim1
      dim2 = array.dim2
      if not dim2:
        # Single dimension variable
        #x = dim1.accept(self)
        x = int(dim1)
        self.lists[var] = [0] * x
      else:
        # Double dimension variable
        x = dim1.accept(self)
        y = dim2.accept(self)
        temp = [0] * y
        v = []
        for i in range(x):
          v.append(temp[:])
        self.tables[var] = v

# --- Expression

  def visit_Group(self, instr:Group):
    return instr.expression.accept(self)

  def visit_Array(self, instr:Array):
    var, dim1, dim2 = instr
    lineno = self.stat[self.pc]
    if not dim1 and not dim2:
      if var in self.vars:
        return self.vars[var]
      else:
        self.error(f"UNDEFINED VARIABLE '{var}' AT LINE {lineno}")
  
    # A list evaluation
    if var in self.lists:
      x = dim1.accept(self)
      if x < 1 or x > len(self.lists[var]):
        self.error(f'LIST INDEX OUT OF BOUNDS AT LINE {lineno}')
      return self.lists[var][x - 1]
      
    if dim1 and dim2:
      if var in self.tables:
        x = dim1.accept(self)
        y = dim2.accept(self)
        if x < 1 or x > len(self.tables[var]) or y < 1 or y > len(self.tables[var][0]):
          self.error(f'TABLE INDEX OUT OUT BOUNDS AT LINE {lineno}')
        return self.tables[var][x - 1][y - 1]

    self.error(f'UNDEFINED VARIABLE {var} AT LINE {lineno}')

  def visit_Logical(self, instr:Logical):
    if(isinstance(instr.left, str)):
      left = self.vars[instr.left]
    elif(isinstance(instr.left, int)):
      left = instr.left
    else:
      left  = instr.left.accept(self)

    if(isinstance(instr.right, str)):
      right = self.vars[instr.right]
    elif(isinstance(instr.right, int)):
      right = instr.right
    else:
      right  = instr.right.accept(self)

    if instr.op == '+':
      (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(instr, left, right)
      return left + right
    elif instr.op == '-':
      self._check_numeric_operands(instr, left, right)
      return left - right
    elif instr.op == '*':
      self._check_numeric_operands(instr, left, right)            
      return left * right
    elif instr.op == '/':
      self._check_numeric_operands(instr, left, right)            
      return left / right
    elif instr.op == '^':
      self._check_numeric_operands(instr, left, right)            
      return math.pow(left, right)
    elif instr.op == '=':
      return left == right
    elif instr.op == '<>':
      return left != right
    elif instr.op == '<':
      self._check_numeric_operands(instr, left, right)            
      return left < right
    elif instr.op == '>':
      self._check_numeric_operands(instr, left, right)            
      return left > right
    elif instr.op == '<=':
      self._check_numeric_operands(instr, left, right)            
      return left <= right
    elif instr.op == '>=':
      self._check_numeric_operands(instr, left, right)            
      return left >= right
    else:
      self.error(f"BAD OPERATOR {instr.op}")
  
  def visit_Binary(self, instr:Binary):
    if(isinstance(instr.left, str)):
      left = self.vars[instr.left]
      if(isinstance(left, str)):
        left = int(left)
    elif(isinstance(instr.left, int)):
      left = instr.left
    else:
      left  = instr.left.accept(self)

    if(isinstance(instr.right, str)):
      right = self.vars[instr.right]
    elif(isinstance(instr.right, int)):
      right = instr.right
    else:
      right  = instr.right.accept(self)

    if instr.op == '+':
      (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(instr, left, right)
      return left + right
    elif instr.op == '-':
      self._check_numeric_operands(instr, left, right)
      return left - right
    elif instr.op == '*':
      self._check_numeric_operands(instr, left, right)            
      return left * right
    elif instr.op == '/':
      self._check_numeric_operands(instr, left, right)            
      return left / right
    elif instr.op == '^':
      self._check_numeric_operands(instr, left, right)            
      return math.pow(left, right)
    elif instr.op == '=':
      return left == right
    elif instr.op == '<>':
      return left != right
    elif instr.op == '<':
      self._check_numeric_operands(instr, left, right)            
      return left < right
    elif instr.op == '>':
      self._check_numeric_operands(instr, left, right)            
      return left > right
    elif instr.op == '<=':
      self._check_numeric_operands(instr, left, right)            
      return left <= right
    elif instr.op == '>=':
      self._check_numeric_operands(instr, left, right)            
      return left >= right
    else:
      self.error(f"BAD OPERATOR {instr.op}")

  def visit_Unary(self, instr:Unary):
    value = instr.expr.accept(self)
    if instr.op == '-':
      self._check_numeric_operand(instr, value)
      return - value

  def visit_Literal(self, instr:Literal):
    return instr.value
  
  def visit_Node(self, instr:Node):
    lineno = self.stat[self.pc]
    print(lineno, instr.__class__.__name__)

  def visit_Number(self, instr:Number):
    return instr.value

  def visit_String(self, instr:String):
    contenido = instr.value
    if isinstance(contenido, Array):
      if contenido.dim1:
        direccion = int(self.vars[contenido.dim1])
      return int(self.lists[contenido.var][direccion])
    if '"' in contenido:
      return contenido
    return int(self.vars[contenido])
  
  def visit_Expression(self, instr:Expression):
    func_type = instr.funcType
    value = instr.exprList
    value = int(value[0].value)

    if func_type in self.functions:
        result = self.functions[func_type](value)
    else:
        result = None  # O mostrar un mensaje de error, etc.

    return result