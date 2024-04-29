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
  def __init__(self, prog, verbose=False):
    self.prog    = prog
    self.verbose = verbose

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
  def interpret(cls, prog:Dict[int, Statement], verbose=False):
    basic = cls(prog, verbose)
    try:
      basic.run()
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
    for lineno in self.stat:
      if isinstance(self.prog[lineno], Data):
        self.data += self.prog[lineno].nlist
    self.dc = 0                  # Initialize the data counter

  # Check for end statements
  def check_end(self):
    has_end = False
    for lineno in self.stat:
      if isinstance(self.prog[lineno], End) and not has_end:
        has_end = lineno
    if not has_end:
      self.error("NO END INSTRUCTION")
    elif has_end != lineno:
      self.error("END IS NOT LAST")

  # Check loops
  def check_loops(self):
    for pc in range(len(self.stat)):
      lineno = self.stat[pc]
      if isinstance(self.prog[lineno], For):
        forinst = self.prog[lineno]
        loopvar = forinst.loopvar
        for i in range(pc + 1, len(self.stat)):
          if isinstance(self.prog[self.stat[i]], Next):
            nextvar = self.prog[self.stat[i]].nextvar
            if nextvar != loopvar:
              continue
            self.loopend[pc] = i
            break
        else:
          self.error(f"FOR WITHOUT NEXT AT LINE {self.stat[pc]}")

  # Change the current line number
  def goto(self, lineno):
    if not lineno in self.prog:
      self.error(f"UNDEFINED LINE NUMBER {lineno} AT LINE {self.stat[self.pc]}")
    self.pc = self.stat.index(lineno)

  # Run it
  def run(self):
    self.vars   = {}       # All variables
    self.lists  = {}       # List variables
    self.tables = {}       # Tables
    self.loops  = []       # Currently active loops
    self.loopend = {}      # Mapping saying where loops end
    self.gosub  = None     # Gosub return point (if any)
    self.column = 0        # Print coñumn control

    self.stat = list(self.prog)  # Ordered list of all line numbers
    self.stat.sort()
    self.pc = 0                  # Current program counter

    # Processing prior to running

    self.collect_data()          # Collect all of the data statements
    self.check_end()
    self.check_loops()

    while True:
      line  = self.stat[self.pc]
      instr = self.prog[line]
      
      try:
        if self.verbose:
          print(line, instr.__class__.__name__)
        instr.accept(self)

      except BasicContinue as e:
        continue
        
      self.pc += 1


  # Assignment
  def assign(self, target, value):
    var, dim1, dim2 = target
    lineno = self.stat[self.pc]
    if not dim1 and not dim2:
      self.vars[var] = value.accept(self)
    elif dim1 and not dim2:
      # List assignment
      x = dim1.accept(self)
      if not var in self.lists:
        self.lists[var] = [0] * 10

      if x > len(self.lists[var]):
        self.error(f"DIMENSION TOO LARGE AT LINE {lineno}")
      self.lists[var][x - 1] = value.accept(self)
    
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

  def visit(self, instr:Remark):
    pass

  def visit(self, instr:Let):
    var   = instr.var
    value = instr.expr
    self.assign(var, value)

  def visit(self, instr:Read):
    for target in instr.exprList:
      if self.dc >= len(self.data):
        # No more data.  Program ends
        raise BasicExit()
      value = self.data[self.dc]
      self.assign(target, value)
      self.dc += 1

  def visit(self, instr:Data):
    pass

  # TODO: variable type
  def visit(self, instr:Input):
    label = instr.label
    if label:
      sys.stdout.write(label)

    for variable in instr.vlist:
      value = input()
      if variable.var[-1] == '$':
        value = String(value)
      else:
        try:
          value = Number(int(value))
        except ValueError:
          value = Number(float(value))
      self.assign(variable, value)
      
  # TODO: %.8g for numeric data. etc
  def visit(self, instr:Print):
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
    if (not items) or items[-1] not in (',', ';'):
      self.newline()
    
  def visit(self, instr:Goto):
    newline = instr.num
    self.goto(newline)
    raise BasicContinue()

  def visit(self, instr:If):
    relexpr = instr.expr
    newline = instr.jumpTo
    if _is_truthy(relexpr.accept(self)):
      self.goto(newline)
      raise BasicContinue()

  def visit(self, instr:For):
    loopvar = instr.ident
    initval = instr.expr0
    finval  = instr.expr1
    stepval = instr.optstep

    # Check to see if this is a new loop
    if not self.loops or self.loops[-1][0] != self.pc:
      # Looks like a new loop. Make the initial assignment
      newvalue = initval
      self.assign(loopvar, initval)
      if not stepval:
        stepval = Number(1)
      stepval = stepval.accept(self)    # Evaluate step here
      self.loops.append((self.pc, stepval))
    else:
      # It's a repeat of the previous loop
      # Update the value of the loop variable according to the
      # step
      stepval = Number(self.loops[-1][1])
      newvalue = Binary('+', loopvar, stepval)

      relop = '>=' if self.loops[-1][1] < 0 else '<='
      if not _is_truthy(Logical(relop, newvalue, finval).accept(self)):
        # Loop is done. Jump to the NEXT
        self.pc = self.loopend[self.pc]
        self.loops.pop()
      else:
        self.assign(loopvar, newvalue)
          
  def visit(self, instr:Next):
    lineno = self.stat[self.pc]
    if not self.loops:
      print(f"NEXT WITHOUT FOR AT LINE {lineno}")
      return
    nextvar = instr.var
    self.pc = self.loops[-1][0]
    loopinst = self.prog[self.stat[self.pc]]
    forvar = loopinst.loopvar
    if nextvar != forvar:
      print(f"NEXT DOESN'T MATCH FOR AT LINE {lineno}")
      return
    raise BasicContinue()

  def visit(self, instr:Union[End, Stop]):
    raise BasicExit()

  def visit(self, instr:DefFunction):
    fname = instr.name
    pname = instr.arguments
    expr  = instr.expresion

    def eval_func(pvalue, name=pname, self=self, expr=expr):
      self.assign(pname, pvalue)
      return expr.accept(self)
    self.functions[fname] = eval_func

  def visit(self, instr:GoSub):
    newline = instr.line
    lineno  = self.stat[self.pc]
    if self.gosub:
      print(f"ALREADY IN A SUBROUTINE AT LINE {lineno}")
      return
    self.gosub = self.stat[self.pc]
    self.goto(newline)
    raise BasicContinue()

  def visit(self, instr:Return):
    lineno = self.stat[self.pc]
    if not self.gosub:
      print(f"RETURN WITHOUT A GOSUB AT LINE {lineno}")
      return
    self.goto(self.gosub)
    self.gosub = None

  def visit(self, instr:Dim):
    for vname, dim1, dim2 in instr.dim:
      if not dim2:
        # Single dimension variable
        x = dim1.accept(self)
        self.lists[vname] = [0] * x
      else:
        # Double dimension variable
        x = dim1.accept(self)
        y = dim2.accept(self)
        temp = [0] * y
        v = []
        for i in range(x):
          v.append(temp[:])
        self.tables[vname] = v

# --- Expression

  def visit(self, instr:Group):
    return instr.expr.accept(self)
  '''
  def visit(self, instr:Bltin):
    name = instr.name
    expr = instr.expr.accept(self)
    return self.functions[name](expr)

  def visit(self, instr:Call):
    name = instr.name
    expr = instr.expr
    return self.functions[name](expr)
  '''
  def visit(self, instr:Array):
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

  def visit(self, instr:Union[Binary,Logical]):
    left  = instr.left.accept(self)
    right = instr.right.accept(self)
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
  
  def visit(self, instr:Unary):
    value = instr.expr.accept(self)
    if instr.op == '-':
      self._check_numeric_operand(instr, value)
      return - value

  def visit(self, instr:Literal):
    return instr.value
  
  def visit(self, instr:Node):
    lineno = self.stat[self.pc]
    print(lineno, instr.__class__.__name__)