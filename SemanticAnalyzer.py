from Nodes import *
from Lexer import Token


############################
## SEMANTIC ANALYZER
############################

class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table = {}

    def register_variable(self, name, value) -> None:
        if name in self.symbol_table:
            raise Exception(f"Variable '{name}' is already declared.")
        data_type = self.get_data_type(value)
        self.symbol_table[name] = data_type

    def analyze(self, node: Node or list[Node, ...]) -> Node or list[Node, ...]:
        if isinstance(node, list):
            for n in node:
                self.analyze(n)

        elif isinstance(node, VarDeclaration):
            if node.name in self.symbol_table:
                raise Exception(f"Variable '{node.name}' is already declared.")
            data_type = self.get_data_type(node.value)
            self.symbol_table[node.name] = data_type
            node.data_type = data_type
            self.analyze(node.value)

        elif isinstance(node, Assignment):
            if node.name not in self.symbol_table:
                raise Exception(f"Variable '{node.name}' is not declared.")
            self.analyze(node.value)

        elif isinstance(node, BinaryOperation):
            self.analyze(node.left)
            self.analyze(node.right)

        elif isinstance(node, Token) and node.type == "IDENTIFIER":
            if node.value not in self.symbol_table:
                raise Exception(f"Variable '{node.value}' is not declared.")

        elif isinstance(node, Token) or isinstance(node, Comment):
            pass

        elif isinstance(node, IfStatement):
            self.analyze(node.condition)
            self.analyze(node.then_body)
            if node.else_body:
                self.analyze(node.else_body)

        elif isinstance(node, WhileStatement):
            self.analyze(node.condition)
            self.analyze(node.body)

        elif isinstance(node, ForStatement):
            for attr in node.attributes:
                attr: Token
                self.register_variable(attr.value, node.value)
            self.analyze(node.value)
            self.analyze(node.body)

        elif isinstance(node, FunctionDeclaration):
            for arg in node.parameters:
                arg: Token
                self.register_variable(arg.value, 0)
            self.analyze(node.body)

        else:
            raise Exception(f"Unknown node type: {type(node)}, {node}")
        return node

    ############################
    ## HELPER FUNCTIONS
    ############################

    def get_data_type(self, node: Node or Token) -> str:
        if isinstance(node, Token):
            if node.type == "IDENTIFIER":
                return self.symbol_table[node.value]
            elif node.type == "INT":
                return "INT"
            elif node.type == "FLOAT":
                return "FLOAT"

        elif isinstance(node, BinaryOperation):
            if node.operator in ("GREATER_THAN", "LESS_THAN", "GREATER_EQUAL", "LESS_EQUAL", "EQUAL", "NOT_EQUAL"):
                return "BOOL"
            if self.get_data_type(node.left) == "INT" and self.get_data_type(node.right) == "INT":
                return "INT"
            return "FLOAT"
        else:
            raise Exception(f"Unknown node type: {type(node)}")
