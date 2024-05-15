# basast.py
from dataclasses import dataclass
from typing import List
from abc import ABC, abstractmethod


# =====================================================================
# EStructura del Arbol de Sintaxis Abstracto (AST)
# =====================================================================

# ---- Expression
@dataclass
class Node:
    def accept(self, visitor):
        return visitor.visit_Node(self)

@dataclass
class Expression(Node):
    def accept(self, visitor):
        return visitor.visit_Expression(self)

@dataclass
class Literal(Expression):
    def accept(self, visitor):
        return visitor.visit_Literal(self)

@dataclass
class String(Literal):
    value: str
    def accept(self, visitor):
        return visitor.visit_String(self)
    
@dataclass
class FnDimName(Literal):
    name: str
    def accept(self, visitor):
        return visitor.visit_FunctionName(self)

@dataclass
class Binary(Expression):
    op   : Expression
    left : Expression
    right: Expression
    def accept(self, visitor):
        return visitor.visit_Binary(self)
 
@dataclass
class Unary(Expression):
    op   : str
    expr : Expression
    def accept(self, visitor):
        return visitor.visit_Unary(self)

@dataclass
class Group(Expression):
    expression: Expression
    def accept(self, visitor):
        return visitor.visit_Group(self)


@dataclass
class Logical(Expression):
    op: Expression
    left: Expression
    right: Expression
    def accept(self, visitor):
        return visitor.visit_Logical(self)
    
@dataclass
class Function(Expression):
    name = FnDimName
    funcType: String
    exprList : List[Expression]
    def accept(self, visitor):
        return visitor.visit_Expression(self)

@dataclass
class Variable(Expression):
    ident: str
    def accept(self, visitor):
        return visitor.visit_Variable(self)
    
@dataclass
class Varlist(Expression):
    ident: Variable
    def accept(self, visitor):
        return visitor.visit_Varlist(self)

@dataclass
class DiscreteNumbers(Literal):
    value: int
    def accept(self, visitor):
        return visitor.visit_DiscreteNumbers(self)

@dataclass
class Array(Expression):
    var: Variable
    dim1: DiscreteNumbers
    dim2: DiscreteNumbers   
    def accept(self, visitor):
        return visitor.visit_Array(self)

@dataclass
class Number(Literal):
    value: int | float
    def accept(self, visitor):
        return visitor.visit_Number(self)

#Nodes
@dataclass
class Statement(Node):
    def accept(self, visitor):
        return visitor.visit_Statement(self)

@dataclass
class Command(Statement):
    line: DiscreteNumbers
    stmt: Statement
    def accept(self, visitor):
        return visitor.visit_Command(self)

# ---- Statements

@dataclass
class Program(Statement):
    statements : List[Statement]
    def accept(self, visitor):
        return visitor.visit_Program(self)


@dataclass
class Let(Statement):
    var : Expression
    expr: Expression
    def accept(self, visitor):
        return visitor.visit_Let(self)

@dataclass
class Read(Statement):
    exprList : List[Expression]
    def accept(self, visitor):
        return visitor.visit_Read(self)

@dataclass
class Data(Statement):
    plist : List[Number|String]
    def accept(self, visitor):
        return visitor.visit_Data(self)

@dataclass
class Goto(Statement):
    num: DiscreteNumbers
    def accept(self, visitor):
        return visitor.visit_Goto(self)

@dataclass
class End(Statement):
    pass
    def accept(self, visitor):
        return visitor.visit_End(self)

@dataclass
class DefFunction(Statement):
    dim : List[FnDimName]
    def accept(self, visitor):
        return visitor.visit_DefFunction(self)

@dataclass
class Print(Statement):
    plist: List[Expression]
    def accept(self, visitor):
        return visitor.visit_Print(self)

@dataclass
class If(Statement):
    expr: Expression
    jumpTo: DiscreteNumbers
    def accept(self, visitor):
        return visitor.visit_If(self)
    
@dataclass
class For(Statement):
    ident: Variable
    expr0: Number
    expr1: Expression | Number
    optstep: DiscreteNumbers
    def accept(self, visitor):
        return visitor.visit_For(self)

@dataclass
class Next(Statement):
    var: Variable
    def accept(self, visitor):
        return visitor.visit_Next(self)

@dataclass
class Remark(Statement):
    comment: String
    def accept(self, visitor):
        return visitor.visit_Remark(self)

@dataclass
class Stop(Statement):
    def accept(self, visitor):
        return visitor.visit_Stop(self)

@dataclass
class Input(Statement):
    vlist: List[Variable]
    def accept(self, visitor):
        return visitor.visit_Input(self)

@dataclass
class Restore(Statement):
    def accept(self, visitor):
        return visitor.visit_Restore(self)

@dataclass
class GoSub(Statement):
    line: DiscreteNumbers
    def accept(self, visitor):
        return visitor.visit_GoSub(self)

@dataclass
class Return(Statement):
    def accept(self, visitor):
        return visitor.visit_Return(self)

@dataclass
class Dim(Statement):
    dim : List[Array]
    def accept(self, visitor):
        return visitor.visit_Dim(self)

#CLASE VISITOR
class Visitor(ABC):
    def visit(self, instr):
       pass
