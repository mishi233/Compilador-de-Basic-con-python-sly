from rich.tree import Tree
from rich.console import Console
from basast import *

class RichASTVisitor:
    def __init__(self):
        self.console = Console()

    def visit_program(self, node: Program, tree: Tree):
        for stmt in node.statements:
            stmt.accept(self, tree)

    def visit_statement(self, node: Statement, tree: Tree):
        pass

    def visit_command(self, node: Command, tree: Tree):
      line_number = f"[blue]{node.line}[/blue]"
      c = tree.add(line_number)
      node.stmt.accept(self, c)

    def visit_let(self, node: Let, tree: Tree):
        let_tree = tree.add("[#00008B] Let")
        var_tree = let_tree.add("Variable")
        node.var.accept(self, var_tree)
        expr_tree = let_tree.add("Expression")
        node.expr.accept(self, expr_tree)

    def visit_variable(self, node: Variable, tree: Tree):
        tree.add(f"Variable: {node.ident}")

    def visit_number(self, node: Number, tree: Tree):
        tree.add(f"Number: {node.value}")

    def visit_remark(self, node: Remark, tree: Tree):
        tree.add(f"Remark: {node.comment}")

    def visit_for(self, node: For, tree: Tree):
      for_tree = tree.add("[#00008B]For")
      ident_tree = for_tree.add("Identifier")
      ident_tree.add(node.ident)
      low_tree = for_tree.add("Low")
      node.expr0.accept(self, low_tree)
      top_tree = for_tree.add("Top")
      node.expr1.accept(self, top_tree)
      if node.optstep:
          step_tree = for_tree.add("Step")
          node.optstep.accept(self, step_tree)
    
    def visit_literal(self, node: Literal, tree: Tree):
        tree.add("Literal")

    def visit_string(self, node: String, tree: Tree):
        tree.add(f": {node.value}")

    def visit_end(self, node: End, tree: Tree):
        tree.add("[#00008B]End")

    def visit_binary(self, node: Binary, tree: Tree):
        binary_tree = tree.add(f"Binary Operation: {node.op}")
        left_tree = binary_tree.add("Left Operand")
        node.left.accept(self, left_tree)
        right_tree = binary_tree.add("Right Operand")
        node.right.accept(self, right_tree)

    def visit_unary(self, node: Unary, tree: Tree):
        unary_tree = tree.add(f"Unary Operation: {node.op}")
        operand_tree = unary_tree.add("Operand")
        node.expr.accept(self, operand_tree)

    def visit_print(self, node: Print, tree: Tree):
        print_tree = tree.add("[#00008B]Print")
        for expr in node.plist:
            expr.accept(self, print_tree)    
    
    def visit_next(self, node: Next, tree: Tree):
        next_tree = tree.add("Next")
        next_tree.add(node.ident) 

    def visit_goto(self, node: Goto, tree: Tree):
        tree.add(f"[#00008B]Goto: {node.num}")

    def visit_return(self, node: Return, tree: Tree):
        tree.add("[#00008B]Return")

    def visit_gosub(self, node: GoSub, tree: Tree):
        tree.add(f"Gosub: line {node.line}")

    def visit_stop(self, node: Stop, tree: Tree):
        tree.add("[#00008B]Stop")

    def visit_dim(self, node: Dim, tree: Tree):
        dim_tree = tree.add("[#00008B]Dim")
        for expr in node.dim:
            expr_tree = dim_tree.add("Expression")
            expr.accept(self, expr_tree)

    def visit_array(self, node: Array, tree: Tree):
        array_tree = tree.add(f"Array: {node.ident}")
        array_tree.add(f"Dim1: {node.dim1}")
        if node.dim2 is not None:
            array_tree.add(f"Dim2: {node.dim2}")

    def visit_read(self, node: Read, tree: Tree):
        read_tree = tree.add("[#00008B]Read")
        for var in node.varlist:
            var_tree = read_tree.add("Variable")
            var.accept(self, var_tree)

    def visit_data(self, node: Data, tree: Tree):
        data_tree = tree.add("[#00008B]Data")
        for num in node.numlist:
            num_tree = data_tree.add("Number")
            num.accept(self, num_tree)

    def visit_if(self, node: If, tree: Tree):
        if_tree = tree.add("[#00008B]If")
        relexpr_tree = if_tree.add("Relational Expression")
        node.expr.accept(self, relexpr_tree)
        if_tree.add(f"Line: {node.jumpTo}")
    
    def visit_fn(self, node: DefFunction, tree: Tree):
        fn_tree = tree.add(f"[#00008B]FN: {node.name}")
        expr_tree = fn_tree.add("Expression")
        node.expresion.accept(self, expr_tree)

    def visit(self, node: Node, tree: Tree):
        method_name = f"visit_{node.__class__.__name__.lower()}"
        visitor_method = getattr(self, method_name, self.default_visit)
        visitor_method(node, tree)

    def default_visit(self, node: Node, tree: Tree):
        tree.add(str(node))







        

def print_ast_tree(node: Node, label: str = "AST") -> Tree:
    tree = Tree(label)
    if isinstance(node, Program):
        for statement in node.statements:
            tree.add(print_ast_tree(statement, "Statement"))
    elif isinstance(node, Command):
        child = Tree(f"Command: {node.line}")
        child.add(print_ast_tree(node.stmt, "Statement"))
        tree.add(child)
    elif isinstance(node, Let):
        child = Tree("Let")
        child.add(Tree(f"variable: {node.var}"))
        child.add(Tree(f"expr:{node.expr}"))
        tree.add(child)
    elif isinstance(node, Remark):
        tree.add(Tree(f"Remark: {node.comment}"))
    elif isinstance(node, Data):
        child = Tree("Data")
        child.add(Tree(f"variable: {node.numlist}"))
        tree.add(child)
    elif isinstance(node, Variable):
        child = Tree("Variable")
        child.add(Tree(f"variable: {node.ident}"))
        tree.add(child)
    elif isinstance(node, Number):
        child = Tree("Number")
        child.add(Tree(f"Number: {node.value}"))
        tree.add(child)
    elif isinstance(node, For):
        child = Tree("For")
        child.add(Tree(f"Ident: {node.ident}"))
        child.add(Tree(f"Expr0: {node.expr0}"))
        child.add(Tree(f"Expr1: {node.expr1}"))
        child.add(Tree(f"optstep: {node.optstep}"))
        tree.add(child)
    elif isinstance(node, End):
        child = Tree("End")
        tree.add(child)
    elif isinstance(node, Literal):
        child = Tree("Literal")
        tree.add(child)
    elif isinstance(node, Number):
        child = Tree("Number")
        child.add(Tree(f"Number: {node.value}"))
        tree.add(child)
    elif isinstance(node, Binary):
        child = Tree("Binary")
        child.add(Tree(f"Left: {node.left}"))
        child.add(Tree(f"Right: {node.right}"))
        tree.add(child)
    elif isinstance(node, Unary):
        child = Tree("Unary")
        child.add(Tree(f"Expr: {node.expr}"))
        tree.add(child)
    elif isinstance(node, Print):
        child = Tree("Print")
        child.add(Tree(f"Plist: {node.plist}"))
        tree.add(child)
    elif isinstance(node, Next):
        child = Tree("Next")
        child.add(Tree(f"Var: {node.var}"))
        tree.add(child)
    elif isinstance(node, Goto):
        child = Tree("Goto")
        child.add(Tree(f"Num: {node.num}"))
        tree.add(child)
    elif isinstance(node, Return):
        child = Tree("Return")
        tree.add(child)
    elif isinstance(node, GoSub):
        child = Tree("GoSub")
        child.add(Tree(f"Line: {node.line}"))
        tree.add(child)
    elif isinstance(node, Stop):
        child = Tree("Stop")
        tree.add(child)
    elif isinstance(node, Dim):
        child = Tree("Dim")
        child.add(Tree(f"DimList: {node.dim}"))
        tree.add(child)
    elif isinstance(node, Read):
        child = Tree("Read")
        child.add(Tree(f"Varlist: {node.varlist}"))
        tree.add(child)
    elif isinstance(node, If):
        child = Tree("If")
        child.add(Tree(f"Expression: {node.expr}"))
        child.add(Tree(f"JumpTo: {node.jumpTo}"))
        tree.add(child)
    elif isinstance(node, For):
        child = Tree("For")
        child.add(Tree(f"Ident: {node.ident}"))
        child.add(Tree(f"Expression 0 : {node.expr0}"))
        child.add(Tree(f"Expression 1: {node.expr1}"))
        child.add(Tree(f"Step: {node.optstep}"))
        tree.add(child)
    elif isinstance(node, DefFunction):
        child = Tree("Def")
        child.add(Tree(f"Name: {node.name}"))
        child.add(Tree(f"Arguments: {node.arguments}"))
        child.add(Tree(f"Expresion: {node.expresion}"))
        tree.add(child)
    return tree