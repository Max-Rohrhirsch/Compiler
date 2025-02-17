######################
## Tokens
######################
class Token:
    def __init__(self, _type, value, line, column) -> None:
        self.type = _type
        self.value = value
        self.line = line
        self.column = column
        self.current_token = None

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"


######################
## Nodes
######################

class Node:
    def __init__(self, _type: str):
        self.type = _type
        self.start_pos: int
        self.end_pos: int


class Comment(Node):
    def __init__(self, value):
        super().__init__("Comment")
        self.value = value

    def __repr__(self):
        return f"Comment('{self.value}')"


class IfStatement(Node):
    def __init__(self, condition, then_body, else_body=None):
        super().__init__("IfStatement")
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def __repr__(self):
        return f"IfStatement(condition = {self.condition}, then_body = {self.then_body}, else_body = {self.else_body})"

class WhileStatement(Node):
    def __init__(self, condition, body):
        super().__init__("WhileStatement")
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement(condition = {self.condition}, body = {self.body})"


class ForStatement(Node):
    def __init__(self, attributes, value, body):
        super().__init__("ForStatement")
        self.attributes: list = attributes
        self.value: any = value
        self.body: list[Node, ...] = body

    def __repr__(self):
        return f"ForStatement(attributes = {self.attributes}, value = {self.value}, body = {self.body})"


class VarDeclaration(Node):
    def __init__(self, name: str, value: any):
        super().__init__("VarDeclaration")
        self.name = name
        self.data_type = None
        self.value = value

    def __repr__(self):
        return f"VarDeclaration({self.data_type} {self.name} = {self.value})"


class Assignment(Node):
    def __init__(self, name: str, value: any):
        super().__init__("Assignment")
        self.name: str = name
        self.value: any = value

    def __repr__(self):
        return f"Assignment(name = {self.name}, value = {self.value})"

class FunctionDeclaration(Node):
    def __init__(self, name: str, return_type: str, parameters: list, body: list):
        super().__init__("FunctionDeclaration")
        self.name: str = name
        self.return_type: str = return_type
        self.parameters: list = parameters
        self.body: list = body

    def __repr__(self):
        return f"FunctionDeclaration({self.return_type} {self.name} ({self.parameters}), body = {self.body})"

class FunctionCall(Node):
    def __init__(self, name: str, arguments: list):
        super().__init__("FunctionCall")
        self.name: str = name
        self.arguments: list = arguments

    def __repr__(self):
        return f"FunctionCall({self.name}({self.arguments}))"

class ReturnStatement(Node):
    def __init__(self, value: any):
        super().__init__("ReturnStatement")
        self.value: any = value

    def __repr__(self):
        return f"ReturnStatement({self.value})"

class BreakStatement(Node):
    def __init__(self):
        super().__init__("BreakStatement")

    def __repr__(self):
        return f"BreakStatement()"

class ContinueStatement(Node):
    def __init__(self):
        super().__init__("ContinueStatement")

    def __repr__(self):
        return f"ContinueStatement()"

class MatchStatement(Node):
    def __init__(self, value: any, cases: list):
        super().__init__("MatchStatement")
        self.value: any = value
        self.cases: list = cases

    def __repr__(self):
        return f"MatchStatement({self.value}, {self.cases})"

class ClassDeclaration(Node):
    def __init__(self, name: str, body: list, is_static=False, is_data_class=False):
        super().__init__("ClassDeclaration")
        self.name: str = name
        self.body: list = body
        self.is_static: bool = is_static
        self.is_data_class: bool = is_data_class

    def __repr__(self):
        return f"ClassDeclaration({self.name}, {self.body})"

class EnumDeclaration(Node):
    def __init__(self, name: str, values: list):
        super().__init__("EnumDeclaration")
        self.name: str = name
        self.values: list = values

    def __repr__(self):
        return f"EnumDeclaration({self.name}, {self.values})"

class ImportStatement(Node):
    def __init__(self, path: str, name:str,  what_to_import: list):
        super().__init__("ImportStatement")
        self.path: str = path
        self.name: str = name
        self.what_to_import: list = what_to_import

    def __repr__(self):
        return f"ImportStatement({self.path})"

class LambdaFunction(Node):
    def __init__(self, parameters: list, body: list):
        super().__init__("LambdaFunction")
        self.parameters: list = parameters
        self.body: list = body

    def __repr__(self):
        return f"LambdaFunction({self.parameters}, {self.body})"


######################
## Special
######################

class BinaryOperation(Node):
    def __init__(self, left: Token or Node, operator, right: Token or Node):
        super().__init__("BinaryOperation")
        self.left: Token or Node = left
        self.operator = operator
        self.right: Token or Node = right

    def __repr__(self):
        return f"BinaryOperation(left = {self.left}, {self.operator}, right = {self.right})"

class UnaryOperation(Node):
    def __init__(self, operator, identifier):
        super().__init__("UnaryOperation")
        self.operator = operator
        self.identifier = identifier

    def __repr__(self):
        return f"UnaryOperation({self.operator}, {self.identifier})"

class Range(Node):
    def __init__(self, start, end, step=None):
        super().__init__("Range")
        self.start = start
        self.end = end
        self.step = step

    def __repr__(self):
        return f"Range({self.start}, {self.end}, {self.step})"

class MatchCase(Node):
    def __init__(self, value: any, return_value: any):
        super().__init__("MatchCase")
        self.value: any = value
        self.return_value: any = return_value

    def __repr__(self):
        return f"MatchCase({self.value}, {self.return_value})"

class EnumValue(Node):
    def __init__(self, name: str, value: any):
        super().__init__("EnumValue")
        self.name: str = name
        self.value: any = value

    def __repr__(self):
        return f"EnumValue({self.name}, {self.value})"

class Attribute(Node):
    def __init__(self, name: str, value: any):
        super().__init__("Attribute")
        self.name: str = name
        self.value: any = value

    def __repr__(self):
        return f"Attribute({self.name}, {self.value})"

