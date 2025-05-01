from Nodes import *
from Lexer import Token


############################
## SEMANTIC ANALYZER
############################

class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table = {}

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
        elif isinstance(node, UnaryOperation):
            if node.identifier not in self.symbol_table:
                raise Exception(f"Variable '{node.identifier}' is not declared.")
        elif isinstance(node, FunctionCall):
            # Simple validation for built-in functions
            if node.name not in ["print", "input", "len"]:
                if node.name not in self.symbol_table:
                    raise Exception(f"Function '{node.name}' is not declared.")
            for arg in node.arguments:
                self.analyze(arg)
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
            # The loop variable is declared inside the loop
            for attr in node.attributes:
                self.symbol_table[attr] = "INT"  # Default iterator type
            
            # Check the iterated value
            if isinstance(node.value, str) and node.value in self.symbol_table:
                pass  # Variable exists
            elif not isinstance(node.value, (int, str)):
                self.analyze(node.value)
                
            self.analyze(node.body)
            
            # Remove the loop variables after the loop
            for attr in node.attributes:
                if attr in self.symbol_table:
                    del self.symbol_table[attr]
        else:
            print(f"Warning: Unknown node type in semantic analyzer: {type(node)}, {node}")
        return node

    ############################
    ## HELPER FUNCTIONS
    ############################

    def get_data_type(self, node: Node or Token) -> str:
        if isinstance(node, Token):
            if node.type == "IDENTIFIER":
                return self.symbol_table.get(node.value, "INT")  # Default to INT if not found
            elif node.type == "INT":
                return "INT"
            elif node.type == "FLOAT":
                return "FLOAT"
            elif node.type == "STRING":
                return "STRING"
            elif node.type == "BOOL":
                return "BOOL"
            else:
                return "INT"  # Default type

        elif isinstance(node, BinaryOperation):
            if node.operator in ("GREATER_THAN", "LESS_THAN", "GREATER_THAN_EQUAL", "LESS_THAN_EQUAL", "EQUAL", "NOT_EQUAL"):
                return "BOOL"
            
            left_type = self.get_data_type(node.left)
            right_type = self.get_data_type(node.right)
            
            if left_type == "FLOAT" or right_type == "FLOAT":
                return "FLOAT"
            return "INT"
        
        elif isinstance(node, FunctionCall):
            # Basic function return type inference
            if node.name == "input":
                return "STRING"
            if node.name == "len":
                return "INT"
            # Default return type
            return "INT"
            
        elif isinstance(node, str):
            return "STRING"
        elif isinstance(node, int):
            return "INT"
        elif isinstance(node, float):
            return "FLOAT"
        elif isinstance(node, bool):
            return "BOOL"
        else:
            return "INT"  # Default type for unknown nodes