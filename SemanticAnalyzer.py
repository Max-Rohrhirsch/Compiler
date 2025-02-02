class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VarDeclaration(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class NumberLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class IfStatement(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.analyze(stmt)
        elif isinstance(node, VarDeclaration):
            if node.name in self.symbol_table:
                raise Exception(f"Variable '{node.name}' is already declared.")
            self.symbol_table[node.name] = True
            self.analyze(node.value)
        elif isinstance(node, Assignment):
            if node.name not in self.symbol_table:
                raise Exception(f"Variable '{node.name}' is not declared.")
            self.analyze(node.value)
        elif isinstance(node, BinaryOperation):
            self.analyze(node.left)
            self.analyze(node.right)
        elif isinstance(node, NumberLiteral):
            pass
        elif isinstance(node, Variable):
            if node.name not in self.symbol_table:
                raise Exception(f"Variable '{node.name}' is not declared.")