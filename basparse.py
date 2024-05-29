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
    
    @_("':' command")
    def statement(self, p):
        return Command(0, p.command)

    #-----------------------------------------
    #-------- DEFINICIÓN DE COMANDOS ---------
    #-----------------------------------------
    @_("LET variable '=' expr")
    def command(self, p):
        return Let(p.variable, p.expr)
    
    @_("LET array '=' expr")
    def command(self, p):
        return Let(p.array, p.expr)

    @_("IDENT")
    def variable(self, p):
        return p.IDENT
    
    @_("array")
    def variable(self, p):
        return p.array

    @_("DATA plist")
    def command(self, p):
        return Data(p.plist)

    @_("PRINT plist")
    def command(self, p):
        return Print(p.plist)

    @_("GOTO INTEGER")
    def command(self, p):
        return Goto(DiscreteNumbers(p.INTEGER))

    @_("IF relexpr THEN expr")
    def command(self, p):
        return If(p.relexpr, DiscreteNumbers(p.expr))
    
    @_("IF relexpr THEN command")
    def command(self, p):
        return If(p.relexpr, Command(0, p.command))

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

    @_("INPUT varlist")
    def command(self, p):
        return Input(p.varlist)

    @_("IDENT { ',' IDENT }")
    def varlist(self, p):
        return ([ p.IDENT0 ] + p.IDENT1)

    @_("DEF FN FN_DIM_NAME '(' exprlist ')' '=' expr")
    def command(self, p):
        return DefFunction(p.FN_DIM_NAME, p.exprlist, p.expr)

    @_("GOSUB INTEGER")
    def command(self, p):
        return GoSub(p.INTEGER)

    @_("RETURN")
    def command(self, p):
        return Return()

    @_("READ varItem { ',' varItem }")
    def command(self, p):
        return Read([ p.varItem0 ] + p.varItem1 )
    
    @_("array")
    def varItem(self, p):
        return [p.array]

    @_("IDENT")
    def varItem(self, p):
        return [p.IDENT]

    @_("DIM array { ',' array }")
    def command(self, p):
        return Dim([ p.array0 ] + p.array1)
    
    @_("IDENT '(' arrayItem ')'")
    def array(self, p):
        return Array(p.IDENT, p.arrayItem, None)

    @_("IDENT '(' arrayItem ',' arrayItem ')'")
    def array(self, p):
        return Array(p.IDENT, p.arrayItem0, p.arrayItem1)
    
    @_("IDENT")
    def arrayItem(self, p):
        return p.IDENT

    @_("INTEGER")
    def arrayItem(self, p):
        return p.INTEGER
    
    @_("empty")
    def arrayItem(self, p):
        pass

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
    
    @_("STRING")
    def expr(self, p):
        return String(p.STRING)
    
    @_("variable")
    def expr(self, p):
        return String(p.variable)

    @_("FUNCTIONS '(' exprlist ')'")
    def expr(self, p):
        return Function(p.FUNCTIONS, p.exprlist) 
    
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

    @_("expr { ',' expr }")
    def exprlist(self, p):
        return [ p.expr0 ] + p.expr1

    @_("expr { optend expr }")
    def plist(self, p):
        return [ p.expr0 ] + p.expr1
    
    @_("expr")
    def plist(self, p):
        return [ p.expr ] 
    
    @_("','")
    def optend(self, p):
        pass

    @_("';'")
    def optend(self, p):
        pass

    @_("STEP expr")
    def optstep(self, p):
        return p.expr

    @_("empty")
    def optstep(self, p):
        pass

    @_("")
    def empty(self, p):
        pass

def test(txt):
    l = Lexer()
    p = Parser()

    top =(p.parse(l.tokenize(txt)))

    print(top)
    #print(print_ast_tree(top))


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("usage: python basparse.py source")
        exit(1)

    test(open(sys.argv[1]).read())