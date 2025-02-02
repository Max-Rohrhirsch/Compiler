from Nodes import *
from Lexer import Token

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node):
        if isinstance(node, list):
            for n in node:
                self.analyze(n)
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
        elif isinstance(node, Token):
            if node.value not in self.symbol_table:
                raise Exception(f"Variable '{node.value}' is not declared.")
        elif isinstance(node, IfStatement):
            self.analyze(node.condition)
            self.analyze(node.then_body)
            if node.else_body:
                self.analyze(node.else_body)
        else:
            raise Exception(f"Unknown node type: {type(node)}, {node}")