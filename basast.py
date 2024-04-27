# basast.py
from dataclasses import dataclass
from typing import List


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
class Binary(Expression):
    op   : str
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
    op: str
    left: Expression
    right: Expression
    def accept(self, visitor):
        return visitor.visit_Logical(self)
    
@dataclass
class Function(Expression):
    funcType: String
    exprList : List[Expression]

@dataclass
class Variable(Expression):
    ident: str
    def accept(self, visitor):
        return visitor.visit_Variable(self)

@dataclass
class Array(Expression):
    ident: str
    indices: tuple
    def accept(self, visitor):
        return visitor.visit_Array(self)

@dataclass
class Number(Literal):
    value: int | float
    def accept(self, visitor):
        return visitor.visit_Number(self)

@dataclass
class DiscreteNumbers(Literal):
    value: int
    def accept(self, visitor):
        return visitor.visit_DiscreteNumbers(self)



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
    name: String
    arguments : List[Expression]
    expresion : Expression
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
    ident: Variable
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
class DimItem(Expression):
    ident: Variable
    tam: List[DiscreteNumbers]
    def accept(self, visitor):
        return visitor.visit_DimItem(self)

@dataclass
class DimList(Expression):
    dimItems : List[DimItem]
    def accept(self, visitor):
        return visitor.visit_DimList(self)
        
    def __iter__(self):
        return iter(self.dimItems)

@dataclass
class Dim(Statement):
    dim : List[DimList]
    def accept(self, visitor):
        return visitor.visit_Dim(self)