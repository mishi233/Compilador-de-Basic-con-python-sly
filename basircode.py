from basast import *
from typing import Dict, Union

class BasicContinue(Exception):
  pass

#El code translator debe de generar código intermedio a partir de la interpretación 
#dada de la grámatica la cual es generada por el barparse.py
class CodeTranslator(Visitor):
    def __init__(self, prog):
        self.prog = prog

    @classmethod
    def translate(cls, prog:Dict[int, Statement]):
        basic = cls(prog)
        basic.generate_code()
        '''
        try:
            basic.generate_code()
        except:
            print("EL CÓDIGO NO HA PODIDO SER GENERADO")
        '''

    def generate_code(self):
        self.stat, self.prog = self.diccionarioDeInstrucciones(self.prog)
        self.pc = 0
        code = []

        while True:
            line  = self.stat[self.pc][0]
            index  = self.stat[self.pc][1]
            instr = self.prog[line][index]

            #print(instr, end="\n")
            #print(self.vars, end="\n\n")
            #print(self.lists, end="\n\n")

            try:
                instr.accept(self)
            except BasicContinue as e:
                continue
                
            self.pc += 1
        
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
    
    