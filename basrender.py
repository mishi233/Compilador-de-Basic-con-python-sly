# basrender.py
from graphviz import Digraph
from basast   import *

class DotRender(Visitor):
    node_default = {
        'shape' : 'box',
        'color' : 'deepskyblue',
        'style' : 'filled',
    }
    edge_default = {
        'arrowhead' : 'none',
    }
    color = 'chartreuse'

    def __init__(self):
        self.dot = Digraph('AST')
        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_default)
        self.seq = 0
    
    def __repr__(self):
        return self.dot.source

    def __str__(self):
        return self.dot.source

    @classmethod
    def render(cls, top: Node):
        dot = cls()
        top.accept(dot)
        return dot.dot, str(dot)
    
    def name(self):
        self.seq += 1
        return f'n{self.seq:02d}'
    
    # Statement Nodes
    def visit_Program(self, n: Program):
        name = self.name()
        self.dot.node(name, label='Program')
        for statement in n.statements:
            self.dot.edge(name, statement.accept(self))
        return name
    
    def inspect_Program(self, n: Program):
        return n.statements
        
    def visit_Command(self, n: Command):
        name = self.name()
        self.dot.node(name, label=f'Command\nLine: {n.line}')
        self.dot.edge(name, n.stmt.accept(self))
        return name

    def visit_Let(self, n: Let):
        name = self.name()
        self.dot.node(name, label='Let')
        self.dot.edge(name, n.expr.accept(self))
        return name

    def visit_Read(self, n: Read):
        name = self.name()
        self.dot.node(name, label='Read')
        return name

    def visit_Input(self, n: Input):
        name = self.name()
        self.dot.node(name, label='Input')
        return name
    
    def visit_Restore(self, n: Input):
        name = self.name()
        self.dot.node(name, label='Input')
        return name

    def visit_Data(self, n: Data):
        name = self.name()
        self.dot.node(name, label='Data')
        for num in n.plist:
            self.dot.edge(name, num.accept(self))
        return name

    def visit_Print(self, n: Print):
        name = self.name()
        self.dot.node(name, label='Print')
        for expr in n.plist:
            self.dot.edge(name, expr.accept(self))
        return name

    def visit_Goto(self, n: Goto):
        name = self.name()
        self.dot.node(name, label=f'Goto\nLine: {n.num.value}')
        return name

    def visit_GoSub(self, n: GoSub):
        name = self.name()
        self.dot.node(name, label=f'Gosub\nLine: {n.line}')
        return name

    def visit_Dim(self, n: Dim):
        name = self.name()
        self.dot.node(name, label='Dim')
        for dim_list in n.dim:
            self.dot.edge(name, dim_list.accept(self))
        return name

    def visit_DefFunction(self, n: DefFunction):
        name = self.name()
        self.dot.node(name, label='Def Function')
        self.dot.edge(name, n.name)
        for argument in n.arguments:
            self.dot.edge(name, argument.accept(self))
        self.dot.edge(name, n.expresion.accept(self))
        return name

    def visit_If(self, n: If):
        name = self.name()
        self.dot.node(name, label='If')
        self.dot.edge(name, n.expr.accept(self))
        self.dot.edge(name, n.jumpTo.accept(self))
        return name

    def visit_For(self, n: For):
        name = self.name()
        self.dot.node(name, label=f'For\nVariable: {n.ident}')
        self.dot.edge(name, n.expr0.accept(self))
        self.dot.edge(name, n.expr1.accept(self))
        if n.optstep:
            self.dot.edge(name, n.optstep.accept(self))
            self.dot.edge(name, f'Optest\nLine: {n.optstep.value}')
        return name

    def visit_Next(self, n: Next):
        name = self.name()
        self.dot.node(name, label=f'Next\nVariable: {n.var}')
        return name

    def visit_End(self, n: End):
        name = self.name()
        self.dot.node(name, label='End')
        return name

    def visit_Remark(self, n: Remark):
        name = self.name()
        self.dot.node(name, label=f'Remark\nComment: {n.comment}')
        return name

    def visit_Stop(self, n: Stop):
        name = self.name()
        self.dot.node(name, label='Stop')
        return name

    def visit_Return(self, n: Return):
        name = self.name()
        self.dot.node(name, label='Return')
        return name

    # Expression Nodes

    def visit_Group(self, n: Group):
        name = self.name()
        self.dot.node(name, label='Group')
        self.dot.edge(name, n.expression.accept(self))
        return name

    def visit_Unary(self, n: Unary):
        name = self.name()
        self.dot.node(name, label=f'Unary\nOperator: {n.op}')
        self.dot.edge(name, n.expr.accept(self))
        return name

    def visit_Literal(self, n: Literal):
        name = self.name()
        self.dot.node(name, label=f'Literal\nValue: {n.value}')
        return name

    def visit_Variable(self, n: Variable):
        name = self.name()
        self.dot.node(name, label=f'Variable\nName: {n.ident}')
        return name

    def visit_Array(self, n: Array):
        name = self.name()
        self.dot.node(name, label=f'Array\nVariable: {n.var}')
        return name
    
    ##-----

    def visit_Binary(self, n: Binary):
        name = self.name()
        self.dot.node(name, label=f'Binary\nOperator: {n.op}')
        self.dot.edge(name, n.left.accept(self))
        self.dot.edge(name, n.right.accept(self))
        return name

    def visit_DiscreteNumbers(self, n: DiscreteNumbers):
        name = self.name()
        self.dot.node(name, label=f'DiscreteNumbers\nValue: {n.value}')
        return name

    def visit_Statement(self, n: Statement):
        name = self.name()
        self.dot.node(name, label='Statement')
        return name

    def visit_Logical(self, n: Logical):
        name = self.name()
        self.dot.node(name, label=f'Logical\nOperator: {n.op}')
        self.dot.edge(name, n.left.accept(self))
        self.dot.edge(name, n.right.accept(self))
        return name

    def visit_Number(self, n: Number):
        name = self.name()
        self.dot.node(name, label=f'Number\nValue: {n.value}')
        return name

    def visit_String(self, n: String):
        name = self.name()
        self.dot.node(name, label=f'String\nValue: {n.value}')
        return name

    def visit_Expression(self, n: Expression):
        name = self.name()
        self.dot.node(name)
        return name
    
    def visit_Node(self, n: Node):
        name = self.name()
        self.dot.node(name)
        return name



#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
class ContentExtractor(Visitor):

    def visit_Program(self, n: Program):
        content = []
        for statement in n.statements:
            content.append(statement.accept(self))
        return content
    
    def visit_Let(self, n: Let):
        content = ['Let']
        content.append(n.var.accept(self))
        content.append(n.expr.accept(self))
        return content

    def visit_Read(self, n: Read):
        content = ['Read']
        for var in n.varlist:
            content.append(var.accept(self))
        return content
    
    def visit_Data(self, n: Data):
        content = ['Data']
        for num in n.numlist:
            content.append(num.accept(self))
        return content

    def visit_Print(self, n: Print):
        content = ['Print']
        for expr in n.plist:
            content.append(expr.accept(self))
        return content

    def visit_Goto(self, n: Goto):
        content = ['Goto']
        content.append(n.num.value)
        return content

    def visit_GoSub(self, n: GoSub):
        content = ['GoSub']
        return content

    def visit_Dim(self, n: Dim):
        content = ['Dim']
        for dim_list in n.dim:
            content.append(dim_list.accept(self))
        return content

    def visit_DefFunction(self, n: DefFunction):
        content = ['Def Function']
        for argument in n.arguments:
            content.append(argument.accept(self))
        content.append(n.expresion.accept(self))
        return content

    def visit_If(self, n: If):
        content = ['If']
        content.append(n.expr.accept(self))
        content.append(n.jumpTo.accept(self))
        return content

    def visit_For(self, n: For):
        content = ['For']
        content.append(n.ident.accept(self))
        content.append(n.expr0.accept(self))
        content.append(n.expr1.accept(self))
        content.append(n.optstep.accept(self))
        content.append(n.optstep.value)
        return content

    def visit_Next(self, n: Next):
        content = ['Next']
        content.append(n.var.accept(self))
        return content

    def visit_End(self, n: End):
        content = ['End']
        return content

    def visit_Remark(self, n: Remark):
        content = ['REM']
        content.append(n.comment.accept(self))
        return content
    
    def visit_Dim(self, n: Dim):
        content = ['Dim']
        for dimList in n.dim:
            content.append(dimList.accept(self))
        return content

    def visit_Stop(self, n: Stop):
        return 'Stop'
    
    def visit_For(self, n: For):
        content = ['For']
        content.append(n.ident.accept(self))
        return content

    def visit_Restore(self, n: Restore):
        return 'Restore'

    def visit_Array(self, n: Array):
        content = ['Array']
        content.append(n.var.accept(self))
        content.append(n.dim1.accept(self))
        content.append(n.dim1.value)
        content.append(n.dim2.accept(self))
        content.append(n.dim2.value)
        return content

    def visit_Binary(self, n: Binary):
        content = ['Binary']
        return content
    
    def visit_Command(self, n: Command):
        content = ['Command']
        return content
    
    def visit_DiscreteNumbers(self, n: DiscreteNumbers):
        content = ['DiscreteNumbers']
        return content
    
    def visit_Expression(self, n: Expression):
        content = ['Expression']
        return content
    
    def visit_Group(self, n: Group):
        content = ['Group']
        return content
    
    def visit_Literal(self, n: Literal):
        content = ['Literal']
        return content
    
    def visit_Logical(self, n: Logical):
        content = ['Logical']
        return content
    
    def visit_Node(self, n: Node):
        content = ['Node']
        return content
    
    def visit_Number(self, n: Number):
        content = ['Number']
        return content
    
    def visit_Statement(self, n: Statement):
        content = ['Statement']
        return content
    
    def visit_Unary(self, n: Unary):
        content = ['Unary']
        return content
    
    def visit_String(self, n: String):
        content = ['String']
        return content
    
    def visit_Variable(self, n: Variable):
        content = ['Variable']
        return content
    
