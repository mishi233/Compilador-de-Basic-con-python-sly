from rich import print
from rich.tree import Tree
import sly

from baslex    import Lexer
from basrender import DotRender
from basast    import *
from graphviz import Digraph
from basrich import print_ast_tree


class Parser(sly.Parser):

    debugfile = 'parse.txt'
    tokens = Lexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', '^'),
        ('right', UMINUS),
    )

    @_("statement { statement }")
    def program(self, p):
        return Program([ p.statement0 ] + p.statement1)

    @_("INTEGER command")
    def statement(self, p):
        return Command(p.INTEGER, p.command)

    #-----------------------------------------
    #-------- DEFINICIÓN DE COMANDOS ---------
    #-----------------------------------------
    @_("LET variable '=' expr")
    def command(self, p):
        return Let(p.variable, p.expr)
    
    @_("READ varlist")
    def command(self, p):
        return Read(p.varlist)

    @_("DATA numlist")
    def command(self, p):
        return Data(p.numlist)

    @_("PRINT plist")
    def command(self, p):
        return Print(p.plist)

    @_("GOTO INTEGER")
    def command(self, p):
        return Goto(DiscreteNumbers(p.INTEGER))

    @_("IF relexpr THEN INTEGER")
    def command(self, p):
        return If(p.relexpr, DiscreteNumbers(p.INTEGER))

    @_("FOR IDENT '=' INTEGER TO expr optstep")
    def command(self, p):
        return For(Variable(p.IDENT), Number(p.INTEGER), p.expr, p.optstep)

    @_("NEXT IDENT")
    def command(self, p):
        return Next(Variable(p.IDENT))

    @_("END")
    def command(self, p):
        return End()

    @_("REM")
    def command(self, p):
        return Remark(p.REM)

    @_("STOP")
    def command(self, p):
        return Stop()

    @_("RESTORE")
    def command(self, p):
        return Restore()

    @_("INPUT IDENT")
    def command(self, p):
        return Input(Variable(p.IDENT))

    @_("DEF FN '(' varlist ')' '=' expr")
    def command(self, p):
        return DefFunction(p.FN, p.varlist, p.expr)

    @_("GOSUB INTEGER")
    def command(self, p):
        return GoSub(p.INTEGER)

    @_("RETURN")
    def command(self, p):
        return Return()

    @_("DIM dimlist")
    def command(self, p):
        return Dim(p.dimlist)

    #-----------------------------------------
    @_("expr '+' expr",
       "expr '-' expr",
       "expr '*' expr",
       "expr '/' expr",
       "expr '^' expr")
    def expr(self, p):
        return Binary(p[1], p.expr0, p.expr1)

    @_("INTEGER")
    def expr(self, p):
        return Number(p.INTEGER)
    
    @_("FLOAT")
    def expr(self, p):
        return Number(p.FLOAT)

    @_("variable")
    def expr(self, p):
        return p.variable
    
    @_("FUNCTIONS '(' funcValue ')'")
    def expr(self, p):
        return Function(p.funcValue)    
    
    @_("'(' expr ')'")
    def expr(self, p):
        return Group(p.expr)

    @_("'-' expr %prec UMINUS")
    def expr(self, p):
        return Unary(p[0], p.expr)

    @_("expr LT expr",
       "expr LE expr",
       "expr GT expr",
       "expr GE expr",
       "expr '=' expr",
       "expr NE expr")
    def relexpr(self, p):
        return Logical(p[1], p.expr0, p.expr1)

    @_("IDENT")
    def variable(self, p):
        return Variable(p.IDENT)

    @_("IDENT '(' INTEGER ')'")
    def variable(self, p):
        return Array(p.IDENT, p.INTEGER)

    @_("IDENT '(' INTEGER ',' INTEGER ')'")
    def variable(self, p):
        return Array(p.IDENT, p.INTEGER0, p.INTEGER1)

    @_("dimitem { ',' dimitem }")
    def dimlist(self, p):
        return DimList([ p.dimitem0 ] + p.dimitem1)

    @_("IDENT '(' size ')'")
    def dimitem(self, p):
        return DimItem(p.IDENT, p.size)

    @_("INTEGER { ',' INTEGER }")
    def size(self, p):
        return [p.INTEGER0] + p.INTEGER1

    @_("variable { ',' variable }")
    def varlist(self, p):
        return [ p.variable0 ] + p.variable1

    @_("number { ',' number }")
    def numlist(self, p):
        return [ p.number0 ] + p.number1 

    @_("INTEGER")
    def number(self, p):
        return Number(p.INTEGER)

    @_("FLOAT")
    def number(self, p):
        return Number(p.FLOAT)

    @_("'-' INTEGER %prec UMINUS")
    def number(self, p):
        return Unary(p[0], Number(p.INTEGER))

    @_("'-' FLOAT %prec UMINUS")
    def number(self, p):
        return Unary(p[0], Number(p.FLOAT))

    @_("INTEGER")
    def funcValue(self, p):
        return Number(p.INTEGER)
    
    @_("FLOAT")
    def funcValue(self, p):
        return Number(p.FLOAT)

    @_("variable")
    def funcValue(self, p):
        return p.variable

    @_("pitem { ',' pitem }")
    def plist(self, p):
        return [ p.pitem0 ] + p.pitem1

    @_("STRING")
    def pitem(self, p):
        return String(p.STRING)

    @_("variable")
    def pitem(self, p):
        return p.variable
    
    '''
    @_("','")
    def optend(self, p):
        pass

    @_("';'")
    def optend(self, p):
        pass

    @_("empty")
    def optend(self, p):
        pass
    '''
    @_("STEP expr")
    def optstep(self, p):
        return p.expr

    @_("empty")
    def optstep(self, p):
        pass

    @_("")
    def empty(self, p):
        pass

    def error(self, p):
        print(p.value)

def test(txt):
    l = Lexer()
    p = Parser()

    top = p.parse(l.tokenize(txt))
    dot, dotstr = DotRender.render(top)

    print(print_ast_tree(top))


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("usage: python basparse.py source")
        exit(1)

    test(open(sys.argv[1]).read())