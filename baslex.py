# coding: utf-8
from rich import print
import sly
import re


class Lexer(sly.Lexer):

    tokens = {
        # keywords
        LET, READ, DATA, PRINT, GOTO, IF,
        THEN, FOR, NEXT, TO, STEP, END,
        STOP, DEF, GOSUB, DIM, REM, RETURN,
        INPUT, RESTORE,

        # operadores de relacion
        LT, LE, GT, GE, NE, 

        # identificador
        IDENT, FN, FUNCTIONS,

        # constantes
        INTEGER, FLOAT, STRING,
    }
    literals = '+-*/^()=:,;'

    # ignorar 
    ignore = r' \t'   

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # expresiones regulares
    @_(r'REM.*\n|rem.*\n')
    def REM(self, t):
        self.lineno += 1
        return t

    @_("LET|let")
    def LET(self, t):
        t.value = t.value.upper()
        return t

    @_("READ|read")
    def READ(self, t):
        t.value = t.value.upper()
        return t

    @_("DATA|data")
    def DATA(self, t):
        t.value = t.value.upper()
        return t

    @_("PRINT|print")
    def PRINT(self, t):
        t.value = t.value.upper()
        return t

    @_("GO ?TO|go ?to")
    def GOTO(self, t):
        t.value = t.value.upper()
        return t

    @_("IF|if")
    def IF(self, t):
        t.value = t.value.upper()
        return t

    @_("THEN|then")
    def THEN(self, t):
        t.value = t.value.upper()
        return t

    @_("FOR|for")
    def FOR(self, t):
        t.value = t.value.upper()
        return t

    @_("NEXT|next")
    def NEXT(self, t):
        t.value = t.value.upper()
        return t

    @_("TO|to")
    def TO(self, t):
        t.value = t.value.upper()
        return t

    @_("STEP|step")
    def STEP(self, t):
        t.value = t.value.upper()
        return t

    @_("END|end")
    def END(self, t):
        t.value = t.value.upper()
        return t

    @_("STOP|stop")
    def STOP(self, t):
        t.value = t.value.upper()
        return t

    @_("DEF|def")
    def DEF(self, t):
        t.value = t.value.upper()
        return t

    @_("GOSUB|gosub")
    def GOSUB(self, t):
        t.value = t.value.upper()
        return t

    @_("DIM|dim")
    def DIM(self, t):
        t.value = t.value.upper()
        return t

    @_("RETURN|return")
    def RETURN(self, t):
        t.value = t.value.upper()
        return t

    @_("INPUT|input")
    def INPUT(self, t):
        t.value = t.value.upper()
        return t

    @_("RESTORE|restore")
    def RESTORE(self, t):
        t.value = t.value.upper()
        return t

    
    FUNCTIONS = r'SIN|sin|COS|cos|TAN|tan|ATN|atn|EXP|exp|ABS|abs|LOG|log|SQR|sqr|RND|rnd|INT|int|TAB|tab|DEG|deg|PI|pi|TIME|time|LEN|len|(LEFT|left|MID|mid|RIGHT|right)\$'
    
    FN    = r'FN[A-Z]|fn[A-Z]'
    IDENT = r'[A-Z][0-9]?\$?'


    LE = r'<='
    GE = r'>='
    NE = r'<>'
    LT = r'<'
    GT = r'>'

    INTEGER = r'\d+'
    FLOAT   = r'(?:\d+(?:\.\d*)?|\.\d+)'
    STRING  = r'"[^"]*"?'

    def error(self, t):
        print(f"Línea [yello]{t.lineno}[/yello]: [red]caracter ilegal '{t.value[0]}'[/red]")
        self.index += 1

def pprint(source):
    from rich.table import Table
    from rich.console import Console

    lex = Lexer()

    table = Table(title='Análisis Léxico')
    table.add_column('type')
    table.add_column('value')
    table.add_column('lineno', justify='right')

    for tok in lex.tokenize(source):
        value = tok.value if isinstance(tok.value, str) else str(tok.value)
        table.add_row(tok.type, value, str(tok.lineno))

    console = Console()
    console.print(table)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('[red]usage: baslex.py filename[/red]')
        sys.exit(1)

    pprint(open(sys.argv[1], encoding='utf-8').read())

