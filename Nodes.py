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


class VarDeclaration(Node):
    def __init__(self, name, value):
        super().__init__("VarDeclaration")
        self.name = name
        self.data_type = None
        self.value = value

    def __repr__(self):
        return f"VarDeclaration({self.data_type} {self.name} = {self.value})"


class Assignment(Node):
    def __init__(self, name, value):
        super().__init__("Assignment")
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assignment(name = {self.name}, value = {self.value})"


class BinaryOperation(Node):
    def __init__(self, left, operator, right):
        super().__init__("BinaryOperation")
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOperation(left = {self.left}, {self.operator}, right = {self.right})"
