from Nodes import *
from Lexer import Token


############################
## SEMANTIC ANALYZER
############################

class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table = {}

    def analyze(self, node):
        """Analyzes an AST node or a list of nodes."""
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
        elif isinstance(node, PropertyAssignment):
            # For property assignments like this.name = value
            # Skip property access semantic checks for now
            self.analyze(node.value)
        elif isinstance(node, ForStatement):
            # For for-loops, add the loop variable to the symbol table
            for attr in node.attributes:
                if attr.name == "name":
                    # Declare the loop variable in the symbol table
                    self.symbol_table[attr.value] = "INT"  # Assume loop variable is integer
            
            # If the value is a Range, analyze it
            if isinstance(node.value, Range):
                self.analyze(node.value.start)
                self.analyze(node.value.end)
                if node.value.step:
                    self.analyze(node.value.step)
            else:
                self.analyze(node.value)
            
            # If it has a body, analyze it
            if hasattr(node, "body") and node.body:
                self.analyze(node.body)
                
            # Clean up the loop variable after analysis
            for attr in node.attributes:
                if attr.name == "name" and attr.value in self.symbol_table:
                    del self.symbol_table[attr.value]
        elif isinstance(node, FunctionCall):
            # Simple validation for built-in functions
            if node.name not in ["print", "input", "len"]:
                # Could add more detailed validation here
                pass
                
            if node.arguments:
                for arg in node.arguments:
                    self.analyze(arg)
        elif isinstance(node, BinaryOperation):
            self.analyze(node.left)
            self.analyze(node.right)
        elif isinstance(node, UnaryOperation):
            if node.identifier not in self.symbol_table:
                raise Exception(f"Variable '{node.identifier}' is not declared.")
        elif isinstance(node, Token) and node.type == "IDENTIFIER":
            if node.value not in self.symbol_table and node.value != "null":  # Special handling for null
                raise Exception(f"Variable '{node.value}' is not declared.")
        elif isinstance(node, IfStatement):
            self.analyze(node.condition)
            self.analyze(node.then_body)
            if node.else_body:
                self.analyze(node.else_body)
        elif isinstance(node, WhileStatement):
            self.analyze(node.condition)
            self.analyze(node.body)
        elif isinstance(node, ClassDeclaration):
            # For class declarations, analyze properties and methods
            if node.properties:
                for prop in node.properties:
                    self.analyze(prop)
            if node.methods:
                for method in node.methods:
                    self.analyze(method)
            if node.constructor:
                self.analyze(node.constructor)
        elif isinstance(node, ConstructorDeclaration):
            # Add parameters to symbol table for constructor body analysis
            temp_symbols = {}
            for param in node.parameters:
                temp_symbols[param] = "PARAM"
                self.symbol_table[param] = "PARAM"
                
            # Analyze the constructor body
            self.analyze(node.body)
            
            # Remove parameters from symbol table
            for param in node.parameters:
                if param in self.symbol_table:
                    del self.symbol_table[param]
        elif isinstance(node, DataclassDeclaration):
            # For dataclass declarations, just validate the field types
            for field in node.fields:
                if field.data_type not in ["INT", "FLOAT", "STRING", "BOOL"] and field.data_type is not None:
                    print(f"Warning: Unknown data type '{field.data_type}' in dataclass field '{field.name}'")
        elif isinstance(node, FunctionDeclaration):
            # Add parameters to symbol table for function body analysis
            temp_symbols = {}
            for param in node.parameters:
                temp_symbols[param] = "PARAM"
                self.symbol_table[param] = "PARAM"
                
            # Analyze the function body
            self.analyze(node.body)
            
            # Remove parameters from symbol table
            for param in node.parameters:
                if param in self.symbol_table:
                    del self.symbol_table[param]
        elif isinstance(node, ReturnStatement):
            self.analyze(node.value)
        elif isinstance(node, MatchStatement):
            self.analyze(node.value)
            for case in node.cases:
                # Use correct attribute names based on the MatchCase class
                if hasattr(case, 'value') and case.value is not None:
                    # Not the else/default case
                    self.analyze(case.value)
                self.analyze(case.return_value)
        elif isinstance(node, Range):
            # For range operations like 1..5
            if hasattr(node, "start") and node.start:
                self.analyze(node.start)
            if hasattr(node, "end") and node.end:
                self.analyze(node.end)
            if hasattr(node, "step") and node.step:
                self.analyze(node.step)
        elif isinstance(node, ImportStatement):
            # Skip import validation for now
            pass
        elif isinstance(node, Comment) or isinstance(node, Token):
            # Skip comments and basic tokens
            pass
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