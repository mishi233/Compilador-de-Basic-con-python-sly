# basircode.py
'''
Una Máquina "Virtual" Intermedia
================================
Una CPU real normalmente consta de registros y un pequeño conjunto básico de 
opcodes  para realizar cálculos matemáticos, cargar/almacenar valores desde 
la memoria y flujo de control básico (ramificaciones, saltos, etc.).
Aunque puedes hacer que un compilador genere instrucciones directamente para 
una CPU, a menudo es más sencillo apuntar a un nivel más alto de abstracción. 
Una de esas abstracciones es la de una máquina de pila.

Las CPU suelen tener un pequeño conjunto de tipos de datos de código, como 
números enteros y flotantes. Hay instrucciones dedicadas para cada tipo. 
El código IR seguirá el mismo principio al admitir operaciones con números 
enteros y de punto flotante.  Por ejemplo:

    ADDI   ; Integer add
    ADDF   ; Float add

Aunque el lenguaje de entrada puede tener otros tipos como 'bool' y 'char', 
esos tipos deben asignarse a números enteros o flotantes. Por ejemplo, un 
bool se puede representar mediante un número entero con valores {0, 1}. 
Un carácter se puede representar mediante un número entero cuyo valor es el 
mismo que el valor del código de carácter (es decir, un código ASCII o un 
punto de código Unicode).

Con eso en mente, aquí hay un conjunto de instrucciones básicas para nuestro 
Código IR:

    ; Operaciones Enteras
    CONSTI  value            ; Push a integer literal on the stack
    ADDI                     ; Add top two items on stack
    SUBI                     ; Substract top two items on stack
    MULI                     ; Multiply top two items on stack
    DIVI                     ; Divide top two items on stack
    ANDI                     ; Bitwise AND
    ORI                      ; Bitwise OR
    LTI                      : <
    LEI                      : <=
    GTI                      : >
    GEI                      : >=
    EQI                      : ==
    NEI                      : !=
    PRINTI                   ; Print top item on stack
    👍
    PEEKI                    ; Get integer from memory (address on stack)
    POKEI                    ; Put integer in memory (value, address) on stack.
    ITOF                     ; Convert integer to float

    ; Operaciones de punto flotante
    CONSTF value             ; Push a float literal
    ADDF                     ; Add top two items on stack
    SUBF                     ; Substract top two items on stack
    MULF                     ; Multiply top two items on stack
    DIVF                     ; Divide top two items on stack
    LTF                      : <
    LEF                      : <=
    GTF                      : >
    GEF                      : >=
    EQF                      : ==
    NEF                      : !=
    PRINTF                   ; Print top item on stack
    👍
    PEEKF                    ; Get float from memory (address on stack)
    POKEF                    ; Put float in memory (value, address on stack) 
    FTOI                     ; Convert float to integer

    👍
    ; Byte-oriented operations (values are presented as integers)    
    PRINTB                   ; Print top item on stack
    PEEKB                    ; Get byte from memory (address on stack)
    POKEB                    ; Put byte in memory (value, address on stack)

    ; Variable load/store.
    ; These instructions read/write both local and global variables. Variables
    ; are referenced by some kind of name that identifies the variable.  The management
    ; and declaration of these names must also be handled by your code generator.
    ; However, variable declarations are not a normal "instruction."  Instead, it's
    ; a kind of data that needs to be associated with a module or function.
    LOCAL_GET name           ; Read a local variable onto stack
    LOCAL_SET name           ; Save local variable from stack
    GLOBAL_GET name          ; Read a global variable onto the stack
    GLOBAL_SET name          ; Save a global variable from the stack

    ; Function call and return.
    ; Functions are referenced by name.   Your code generator will need to figure
    ; out some way to manage these names.
    👍
    CALL name                ; Call function. All arguments must be on stack
    RET                      ; Return from a function. Value must be on stack

    ; Structured control flow
    IF                       ; Start consequence part of an "if". Test on stack
    ELSE                     ; Start alternative part of an "if".
    ENDIF                    ; End of an "if" statement.

    LOOP                     ; Start of a loop
    CBREAK                   ; Conditional break. Test on stack.
    CONTINUE                 ; Go back to loop start
    ENDLOOP                  ; End of a loop

    ; Memory
    👍
    GROW                     ; Increment memory (size on stack) (returns new size)

Una palabra sobre el acceso a la memoria... las instrucciones PEEK y POKE se 
utilizan para acceder a direcciones de memoria sin procesar. Ambas instrucciones 
requieren que una dirección de memoria esté en la pila *primero*. Para la 
instrucción POKE, el valor que se almacena se inserta después de la dirección. 
El orden es importante y es fácil estropearlo. Así que preste mucha atención a eso.
'''
from basast import *
from interp import Interpreter

#python basic.py -T programs/lin_solver.bas
class CodeTranslator(Visitor):
    def __init__(self):
        self.prog = []
        self.variablesAuxiliares = {}
        self.funcionesPropias = {}
        self.ponerConsequenteIf = []
        self.funcionesArgumentos = []

    def intermedium_code(self, prog):
        command_dict = {}

        for command in prog.statements:
            command_dict[int(command.line)] = command.stmt

        #particiones = self.revisionGoto(command_dict)
        
        codigoIntermedio = []
        for key in command_dict.keys():
            if key in self.ponerConsequenteIf:
                codigoIntermedio += [['ELSE']]
            if key-1 in self.ponerConsequenteIf:
                codigoIntermedio += [['ENDIF']]
            codigoIntermedio += command_dict[key].accept(self)

        self.correcionesDeTipos(codigoIntermedio)
        funcionesAIncluir = self.incluirFunciones(codigoIntermedio)
        
        #for code in codigoIntermedio:
        #    print(code)

        interpretadorCI = Interpreter()

        for key in funcionesAIncluir.keys():
            interpretadorCI.add_function(key, funcionesAIncluir[key][1], funcionesAIncluir[key][0])

        interpretadorCI.add_function('_init', [], codigoIntermedio)
        interpretadorCI.execute('_init')

    # - - - - - IMPLEMENTACIÓN DE FUNCIONES INTERNAS - - - - -
    def revisionGoto(self, command_dict):
        particiones = {}
        for key in command_dict.keys():
            if isinstance(command_dict[key], Goto):
                if int(command_dict[key].num.value) not in command_dict.keys():
                    return False
                particiones[key] = int(command_dict[key].num.value)
        return particiones        
    
    def correcionesDeTipos(self, code):
        index = 0
        opPuntoFlotante = ['ADDF', 'SUBF', 'MULF', 'DIVF', 'EQF', 'NEF', 'LTF', 'GTF', 'LEF', 'GEF']

        while index < len(code) - 1:
            if code[index][0] == 'CONSTI' and code[index+1][0] in opPuntoFlotante:
                code.insert(index+1, ['ITOF'])
                index += 2 
            else:
                index += 1

    def incluirFunciones(self, code):
        funcionesPosibles = ['SIN', 'COS', 'TAN', 'ATN', 'EXP', 'ABS', 'LOG', 'SQR', 'INT', 'DEG', 'PI']
        funcionesExistentes = []
        funcionesAIncluir = {}

        for statement in code:
            if statement[0] == 'CALL':
                if statement[1] in funcionesPosibles:
                    funcionesExistentes.append([statement[1], self.funcionesArgumentos[0]])
                    self.funcionesArgumentos.pop()
                else:
                    funcionesAIncluir[statement[1]] = self.funcionesPropias[statement[1]]
                    

                    
        for funcion in funcionesExistentes: 
            if funcion[0] == 'SIN':
                funcionesAIncluir['FAC'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'Z'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', 'RSL'],
                    ['LOCAL_GET', 'FIN'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],
                    
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET']
                ], 'Z'
                
                funcionesAIncluir['ELV'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'EXPO'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_GET', 'RSL'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],

                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],
                ], [funcion[1], 'EXPO']

                funcionesAIncluir['SIN'] = [ 

                    ['CONSTI', 0],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 0],
                    ['LOCAL_SET', 'OP'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 30],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],
                        ['LOCAL_SET', 'RSL_EXP'],

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'FAC'],
                        ['LOCAL_SET', 'RSL_FAC'],

                        ['LOCAL_GET', 'RSL_EXP'],
                        ['LOCAL_GET', 'RSL_FAC'],                        
                        ['DIVF'],

                        ['LOCAL_GET', 'OP'],
                        ['CONSTI', 0],
                        ['EQI'],
                        ['IF'], 
                            ['ADDF'],
                            ['CONSTI', 1],
                            ['LOCAL_SET', 'OP'],
                        ['ELSE'],
                            ['SUBF'],
                            ['CONSTI', 0],
                            ['LOCAL_SET', 'OP'],
                        ['ENDIF'],

                        ['LOCAL_SET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 2],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],

                ], [funcion[1]]

            if funcion[0] == 'COS':
                funcionesAIncluir['FAC'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'Z'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', 'RSL'],
                    ['LOCAL_GET', 'FIN'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],
                    
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET']
                ], 'Z'
                
                funcionesAIncluir['ELV'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'EXPO'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_GET', 'RSL'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],

                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],
                ], [funcion[1], 'EXPO']

                funcionesAIncluir['COS'] = [ 

                    ['CONSTI', 1],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'OP'],

                    ['CONSTI', 2],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 30],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],
                        ['LOCAL_SET', 'RSL_EXP'],

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'FAC'],
                        ['LOCAL_SET', 'RSL_FAC'],

                        ['LOCAL_GET', 'RSL_EXP'],
                        ['LOCAL_GET', 'RSL_FAC'],                        
                        ['DIVF'],

                        

                        ['LOCAL_GET', 'OP'],
                        ['CONSTI', 0],
                        ['EQI'],
                        ['IF'], 
                            ['ADDF'],
                            ['CONSTI', 1],
                            ['LOCAL_SET', 'OP'],
                        ['ELSE'],
                            ['SUBF'],
                            ['CONSTI', 0],
                            ['LOCAL_SET', 'OP'],
                        ['ENDIF'],


                        ['LOCAL_SET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 2],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],

                ], [funcion[1]]

            if funcion[0] == 'TAN':
                funcionesAIncluir['FAC'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'Z'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', 'RSL'],
                    ['LOCAL_GET', 'FIN'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],
                    
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET']
                ], 'Z'
                
                funcionesAIncluir['ELV'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'EXPO'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_GET', 'RSL'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],

                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],
                ], [funcion[1], 'EXPO']

                funcionesAIncluir['SIN'] = [ 

                    ['CONSTI', 0],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 0],
                    ['LOCAL_SET', 'OP'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 30],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],
                        ['LOCAL_SET', 'RSL_EXP'],

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'FAC'],
                        ['LOCAL_SET', 'RSL_FAC'],

                        ['LOCAL_GET', 'RSL_EXP'],
                        ['LOCAL_GET', 'RSL_FAC'],                        
                        ['DIVF'],

                        ['LOCAL_GET', 'OP'],
                        ['CONSTI', 0],
                        ['EQI'],
                        ['IF'], 
                            ['ADDF'],
                            ['CONSTI', 1],
                            ['LOCAL_SET', 'OP'],
                        ['ELSE'],
                            ['SUBF'],
                            ['CONSTI', 0],
                            ['LOCAL_SET', 'OP'],
                        ['ENDIF'],


                        ['LOCAL_SET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 2],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],

                ], [funcion[1]]

                funcionesAIncluir['COS'] = [ 

                    ['CONSTI', 1],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'OP'],

                    ['CONSTI', 2],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 30],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],
                        ['LOCAL_SET', 'RSL_EXP'],

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'FAC'],
                        ['LOCAL_SET', 'RSL_FAC'],

                        ['LOCAL_GET', 'RSL_EXP'],
                        ['LOCAL_GET', 'RSL_FAC'],                        
                        ['DIVF'],

                        

                        ['LOCAL_GET', 'OP'],
                        ['CONSTI', 0],
                        ['EQI'],
                        ['IF'], 
                            ['ADDF'],
                            ['CONSTI', 1],
                            ['LOCAL_SET', 'OP'],
                        ['ELSE'],
                            ['SUBF'],
                            ['CONSTI', 0],
                            ['LOCAL_SET', 'OP'],
                        ['ENDIF'],


                        ['LOCAL_SET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 2],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],

                ], [funcion[1]]

                funcionesAIncluir['TAN'] = [
                    ['LOCAL_GET', funcion[1]],  
                    ['CALL', 'SIN'],     
                    ['LOCAL_SET', 'SINX'], 

                    ['LOCAL_GET', funcion[1]],  
                    ['CALL', 'COS'],     
                    ['LOCAL_SET', 'COSX'], 

                    ['LOCAL_GET', 'SINX'],  
                    ['LOCAL_GET', 'COSX'], 
                    ['DIVF'],               
                    ['RET'],       
                ], [funcion[1]]

            if funcion[0] == 'ATN':
                funcionesAIncluir['ELV'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'EXPO'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_GET', 'RSL'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],

                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],
                ], [funcion[1], 'EXPO']

                funcionesAIncluir['ATN'] = [
                    ['CONSTI', 0],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 0],
                    ['LOCAL_SET', 'OP'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 5],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],
                        ['LOCAL_SET', 'RSL_EXP'],

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', 'RSL_EXP'],
                        ['LOCAL_GET', 'ACT'],                        
                        ['DIVF'],

                        ['LOCAL_GET', 'OP'],
                        ['CONSTI', 0],
                        ['EQI'],
                        ['IF'], 
                            ['ADDF'],
                            ['CONSTI', 1],
                            ['LOCAL_SET', 'OP'],
                        ['ELSE'],
                            ['SUBF'],
                            ['CONSTI', 0],
                            ['LOCAL_SET', 'OP'],
                        ['ENDIF'],

                        ['LOCAL_SET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 2],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],

                ], [funcion[1]]

            if funcion[0] == 'EXP':
                funcionesAIncluir['FAC'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'Z'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', 'RSL'],
                    ['LOCAL_GET', 'FIN'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],
                    
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET']
                ], 'Z'
                
                funcionesAIncluir['ELV'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'EXPO'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_GET', 'RSL'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],

                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],
                ], [funcion[1], 'EXPO']

                funcionesAIncluir['EXP'] = [ 

                    ['CONSTI', 1],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 30],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],
                        ['LOCAL_SET', 'RSL_EXP'],

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'FAC'],
                        ['LOCAL_SET', 'RSL_FAC'],

                        ['LOCAL_GET', 'RSL_EXP'],
                        ['LOCAL_GET', 'RSL_FAC'],                        
                        ['DIVF'],

                        ['ADDF'],

                        ['LOCAL_SET', 'RSL'],

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 1],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],

                ], [funcion[1]]           
           
            if funcion[0] == 'ABS':
                funcionesAIncluir['ABS'] = [ 
                    
                    ['LOCAL_GET', funcion[1]],
                    ['CONSTI', 0],
                    ['GTI'],
                    ['IF'],
                    ['LOCAL_GET', funcion[1]],
                    ['RET'] ,
                    ['ELSE'],
                    ['LOCAL_GET', funcion[1]],
                    ['CONSTI', -1],
                    ['MULF'],
                    ['RET'],
                    ['ENDIF'],

                ], [funcion[1]] 

            if funcion[0] == 'INT':
                funcionesAIncluir['INT'] = [ 
                    
                    ['LOCAL_GET', funcion[1]],
                    ['FTOI'],
                    ['RET'],

                ], [funcion[1]]

            if funcion[0] == 'PI':
                funcionesAIncluir['PI'] = [ 
                    ['LOCAL_GET', funcion[1]],
                    ['CONSTF', 3.141592],
                    ['MULF'],
                    ['RET'],
                ], [funcion[1]] 

            if funcion[0] == 'DEG':
                funcionesAIncluir['DEG'] = [ 
                    ['CONSTF', 180.0],
                    ['CONSTF', 3.141592],
                    ['DIVF'],
                    ['LOCAL_GET', funcion[1]],
                    ['MULF'],
                    ['RET'],
                ], [funcion[1]]

            if funcion[0] == 'SQR':
                funcionesAIncluir['SQR'] = [ 
                    
                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_SET', 'APROX'],

                    ['CONSTI', 0],
                    ['LOCAL_SET', 'ACT'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 30],         
                        ['GTI'],                
                        ['CBREAK'],

                        ['LOCAL_GET', funcion[1]],
                        ['LOCAL_GET', 'APROX'],
                        ['DIVF'],
                        ['LOCAL_GET', 'APROX'],
                        ['ADDF'],
                        ['CONSTF', 0.5],
                        ['MULF'],
                        ['LOCAL_SET', 'APROX'],                        

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 1], 
                        ['ADDI'],
                        ['LOCAL_SET', 'ACT'],

                    ['ENDLOOP'],

                    ['LOCAL_GET', 'APROX'],
                    ['RET'],

                ], [funcion[1]] 

            if funcion[0] == 'LOG':
               
                funcionesAIncluir['ELV'] = [
                    ['CONSTI', 1],
                    ['LOCAL_SET', 'FIN'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'RSL'],

                    ['LOOP'],
                    ['LOCAL_GET', 'FIN'],
                    ['LOCAL_GET', 'EXPO'],
                    ['GTI'],
                    ['CBREAK'],

                    ['LOCAL_GET', funcion[1]],
                    ['LOCAL_GET', 'RSL'],
                    ['MULI'],
                    ['LOCAL_SET', 'RSL'],

                    ['LOCAL_GET', 'FIN'],
                    ['CONSTI', 1],
                    ['ADDI'],
                    ['LOCAL_SET', 'FIN'],

                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['RET'],
                ], [funcion[1], 'EXPO']

                funcionesAIncluir['LN'] = [ 

                    ['CONSTI', 0],              
                    ['LOCAL_SET', 'RSL'],

                    ['CONSTI', 0],
                    ['LOCAL_SET', 'OP'],

                    ['CONSTI', 1],
                    ['LOCAL_SET', 'ACT'],


                    ['CONSTI', 0],
                    ['LOCAL_SET', 'LNX'],


                    ['LOOP'],
    
                        ['CONSTI', 2],
                        ['LOCAL_GET', funcion[1]],
                        ['GEF'],
                        ['CBREAK'],

                        ['LOCAL_GET', funcion[1]],
                        ['CONSTI', 2.718281],
                        ['DIVF'],
                        ['LOCAL_SET', funcion[1]],

                        ['LOCAL_GET', 'LNX'],
                        ['CONSTI', 1],
                        ['ADDI'],
                        ['LOCAL_SET', 'LNX'],

                    ['ENDLOOP'],

                    ['LOOP'],

                        ['LOCAL_GET', 'ACT'],   
                        ['CONSTI', 10],         
                        ['GTI'],                
                        ['CBREAK'], 

                        ['LOCAL_GET', 'RSL'],

                        ['LOCAL_GET', funcion[1]],
                        ['CONSTI', 1],  
                        ['SUBI'],
                        ['LOCAL_GET', 'ACT'],
                        ['CALL', 'ELV'],

                        ['LOCAL_GET', 'ACT'],                        
                        ['DIVF'],                      

                        ['LOCAL_GET', 'OP'],
                        ['CONSTI', 0],
                        ['EQI'],
                        ['IF'], 
                            ['ADDF'],
                            ['CONSTI', 1],
                            ['LOCAL_SET', 'OP'],
                        ['ELSE'],
                            ['SUBF'],
                            ['CONSTI', 0],
                            ['LOCAL_SET', 'OP'],
                        ['ENDIF'],

                        ['LOCAL_SET', 'RSL'],   

                        ['LOCAL_GET', 'ACT'],
                        ['CONSTI', 1],       
                        ['ADDI'],            
                        ['LOCAL_SET', 'ACT'],
                        
                    ['ENDLOOP'],
                    ['LOCAL_GET', 'RSL'],
                    ['LOCAL_GET', 'LNX'],
                    ['ADDI'],

                    ['RET'],

                ], [funcion[1]]

                funcionesAIncluir['LOG'] = [ 

                    ['LOCAL_GET', funcion[1]],
                    ['CALL', 'LN'],
                    ['CONSTF', 2.3025],
                    ['DIVF'],
                    ['RET']

                ], [funcion[1]]

        return funcionesAIncluir
                

    # - - - - - IMPLEMENTACIÓN DE GENERACIÓN DE CÓDIGO INTERMEDIO - - - - -
    def visit_Let(self, instr:Let):
        var = instr.var
        expr = instr.expr.accept(self)
        return expr + [['LOCAL_SET',var]] 
    
    def visit_Print(self, instr:Print):
        code = []
        for pitem in instr.plist:
            code = code + pitem.accept(self) + [['PRINTI']]
        return code
    
    def visit_Number(self, instr:Number):
        value = instr.value
        if '.' in value:
            return [[f'CONSTF', float(value)]]
        else:
            return [[f'CONSTI', int(value)]]
    
    def visit_DiscreteNumbers(self, instr:DiscreteNumbers):
        return instr.value.accept(self)[0][1]

    def visit_Goto(self, instr:Goto):
        return ["FALTA EL SALTO"]
    
    def visit_Variable(self, instr:Variable):
        return [['LOCAL_GET' ,instr.ident]]
    
    def visit_Expression(self, instr:Variable):
        code = []
        funcionInstruccion = instr.funcType
        
        for expr in instr.exprList:
            code += expr.accept(self)
            self.funcionesArgumentos.append(expr.ident)
        code += [['CALL', funcionInstruccion]]

        return code

    def visit_If(self, instr:If):
        jump = instr.jumpTo.accept(self)
        self.ponerConsequenteIf.append(jump)

        expr = instr.expr.accept(self)
        
        return expr + [['IF']]
    
    def visit_For(self, instr:For):
        code = []
        var = instr.ident.accept(self)[0][1]
        result = instr.optstep
        if isinstance(result, Unary):
            self.variablesAuxiliares[var] = int(str(result.op) + str(result.expr.accept(self)[0][1]))
        elif result is None:
            self.variablesAuxiliares[var] = 1
        else:
            self.variablesAuxiliares[var] = int(result.accept(self)[0][1])

        code += instr.expr0.accept(self)
        code += [['LOCAL_SET',var]]
        code += [['LOOP']]
        code += instr.ident.accept(self)
        code += instr.expr1.accept(self)
        code += [['EQI']]
        code += [['CBREAK']]

        return code

    def visit_Next(self, instr:Next):
        code = []
        var = instr.var.accept(self)[0][1]
        opStep = self.variablesAuxiliares[var]        
        
        code += instr.var.accept(self)
        if opStep < 0:
            code += [['CONSTI', opStep*-1]]
            code += [['SUBI']]
        else: 
            code += [['CONSTI', opStep]]
            code += [['ADDI']]

        code += [['LOCAL_SET', var]]
        code += [['ENDLOOP']]

        return code
    
    def visit_DefFunction(self, instr: DefFunction):
        nombreDeLaFuncion = instr.functionName
        argumentos = []

        for arg in instr.arguments:
            argumentos.append(arg.accept(self)[0][1])   

        self.funcionesPropias[nombreDeLaFuncion] = instr.expr.accept(self) + [['RET']] , argumentos
    
        return []
    
    def visit_Logical(self, instr:Logical):
        operator = instr.op
        left = instr.left.accept(self)
        right = instr.right.accept(self)
                                   
        if operator == '+':
            return left + right + [['ADDI']]
        elif operator == '-':
            return left + right + [['SUBI']]
        elif operator == '*':
            return left + right + [['MULI']]
        elif operator == '/':
            return left + right + [['DIVI']]
        elif operator == '=':
            return left + right + [['EQI']]
        elif operator == '<>':
            return left + right + [['NEI']]
        elif operator == '<':
            return left + right + [['LTI']]
        elif operator == '>':
            return left + right + [['GTI']]
        elif operator == '<=':
            return left + right + [['LEI']]
        elif operator == '>=':
            return left + right + [['GEI']]
        else:
            self.error(f"BAD OPERATOR {instr.op}")

    def visit_Binary(self, instr: Binary):
        operator = instr.op
        left = instr.left.accept(self)
        right = instr.right.accept(self)
        
        if left[len(left)-1][0][-1] == 'F' or right[0][0][-1] == 'F':
            if operator == '+':
                return left + right + [['ADDF']]
            elif operator == '-':
                return left + right + [['SUBF']]
            elif operator == '*':
                return left + right + [['MULF']]
            elif operator == '/':
                return left + right + [['DIVF']]
            elif operator == '=':
                return left + right + [['EQF']]
            elif operator == '<>':
                return left + right + [['NEF']]
            elif operator == '<':
                return left + right + [['LTF']]
            elif operator == '>':
                return left + right + [['GTF']]
            elif operator == '<=':
                return left + right + [['LEF']]
            elif operator == '>=':
                return left + right + [['GEF']]
            else:
                self.error(f"BAD OPERATOR {instr.op}") 
        else:
            if operator == '+':
                return left + right + [['ADDI']]
            elif operator == '-':
                return left + right + [['SUBI']]
            elif operator == '*':
                return left + right + [['MULI']]
            elif operator == '/':
                return left + right + [['DIVI']]
            elif operator == '=':
                return left + right + [['EQI']]
            elif operator == '<>':
                return left + right + [['NEI']]
            elif operator == '<':
                return left + right + [['LTI']]
            elif operator == '>':
                return left + right + [['GTI']]
            elif operator == '<=':
                return left + right + [['LEI']]
            elif operator == '>=':
                return left + right + [['GEI']]
            else:
                self.error(f"BAD OPERATOR {instr.op}")
        
    def visit_End(self, instr:End):
        return [['CONSTI',0],['RET']]
    
    def visit_Remark(self, instr:Remark):
        return []
    
    def visit_Unary(self, instr: Unary):
        num = instr.expr.accept(self)
        if isinstance(num[0][1], float):
            return [[num[0][0], float(instr.op+str(num[0][1]))]]
        else:
            return [[num[0][0], int(instr.op+str(num[0][1]))]]