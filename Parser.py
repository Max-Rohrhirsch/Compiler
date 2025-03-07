############################
## DOCUMENTATION
############################
"""
Keywords = [
    "IF",
    "ELSE",
    "WHILE",
    "FOR",
    "BREAK",
    "RETURN",
    "FUNCTION",
    "VAR",
    "CONST",
    "TRUE",
    "FALSE",
]

Operators = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MUL",
    "/": "DIV",
    "%": "MOD",
    "=": "ASSIGN",
    "==": "EQUAL",
    "!=": "NOT_EQUAL",
    "<": "LESS_THAN",
    ">": "GREATER_THAN",
    "<=": "LESS_THAN_EQUAL",
    ">=": "GREATER_THAN_EQUAL",
    "&&": "AND",
    "||": "OR",
    "!": "NOT",
}

Symbols = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ";": "SEMICOLON",
    ":": "COLON",
    ".": "DOT",
}
"""

############################
## Parser class
############################

from Nodes import *
from Lexer import Token


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0  # Current token index

    def peek(self, step=0) -> Token:
        """Returns the current token without consuming it."""
        return self.tokens[self.current+step] if (self.current+step) < len(self.tokens) else None

    def advance(self) -> None:
        """Moves to the next token."""
        self.current += 1

    def match_set(self, expected_type: tuple[str, ...]) -> bool:
        for expected_type in expected_type:
            if self.peek() and self.peek().type == expected_type:
                self.advance()
                return True
        return False

    def match(self, expected_type: str, expected_value=None) -> bool:
        """Consumes the token if it matches the expected type."""
        if self.peek() and self.peek().type == expected_type and (
                expected_value is None or self.peek().value == expected_value):
            self.advance()
            return True
        return False

    def consume(self, expected_type: str) -> Token:
        """Consume a token and move to the next."""
        token = self.peek()
        if token is None or token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but got {token.type if token else 'EOF'}")
        self.current += 1
        return token

    def make_body(self) -> list[Node]:
        self.consume("LBRACE")
        then_body = []
        while self.peek() and self.peek().type != "RBRACE":
            then_body.append(self.statement())
        self.consume("RBRACE")
        return then_body

    ############################
    ## MAIN FUNCTION
    ############################

    def parse(self) -> list[Node]:
        """Entry point for parsing: Parses a full program."""
        statements = []
        while self.peek().type != "EOF":
            statements.append(self.statement())
        return statements

    ############################
    ## MAKER FUNCTIONS
    ############################

    def statement(self) -> Node:
        """Parses statements like variable declarations and assignments."""
        if self.match("KEYWORD", "VAR"):
            return self.var_declaration()
        if self.peek(0).type == "IDENTIFIER":
            if self.peek(1).type == "LPAREN":
                return self.function_call()
            return self.assignment()  # OR function call
        if self.match("KEYWORD", "IF"):
            return self.if_statement()
        if self.peek().type == "COMMENT":
            return Comment(self.consume("COMMENT").value)
        if self.match("KEYWORD", "WHILE"):
            return self.while_statement()
        if self.match("KEYWORD", "FOR"):
            return self.for_statement()
        if self.match("KEYWORD", "FUNCTION"):
            return self.function_declaration()
        if self.match("KEYWORD", "RETURN"):
            return self.return_statement()
        raise SyntaxError("Invalid statement" + str(self.peek()))

    def var_declaration(self) -> VarDeclaration:
        """Parses: var x = 10;"""
        name = self.consume("IDENTIFIER").value
        self.consume("ASSIGN")
        value = self.expression()
        return VarDeclaration(name, value)

    def assignment(self) -> Assignment:
        """Parses: x = 10;"""
        name = self.consume("IDENTIFIER").value
        self.consume("ASSIGN")
        value = self.expression()
        return Assignment(name, value)

    def if_statement(self) -> IfStatement:
        """Parses an if-statement into an AST node."""
        # self.consume("IF")

        self.consume("LPAREN")
        condition = self.expression()
        self.consume("RPAREN")

        then_body = self.make_body()
        else_body = None
        if self.peek() and self.peek().type == "ELSE":
            self.consume("ELSE")

            then_body = self.make_body()

        return IfStatement(condition, then_body, else_body)

    def while_statement(self) -> WhileStatement:
        """Parses a while-statement into an AST node."""
        self.consume("LPAREN")
        condition = self.expression()
        self.consume("RPAREN")

        body = self.make_body()
        return WhileStatement(condition, body)

    def for_statement(self) -> ForStatement:
        """Parses a for-statement into an AST node."""
        attributes = [self.consume("IDENTIFIER")]

        while self.match("COMMA"):
            attributes.append(self.consume("IDENTIFIER"))

        if not self.match("KEYWORD", "IN"):
            raise SyntaxError("Expected 'in' keyword in for loop")

        if self.peek().type == "INT":
            if self.peek(1).type == "RANGE":
                value = self.range_expression()
            else:
                value = self.consume("INT")
        elif self.peek().type == "IDENTIFIER":
            value = self.consume("IDENTIFIER")
        else:
            raise SyntaxError("Expected a number or variable")

        self.consume("LBRACE")
        body = []
        while self.peek() and self.peek().type != "RBRACE":
            body.append(self.statement())
        self.consume("RBRACE")
        return ForStatement(attributes, value, body)

    def function_declaration(self) -> FunctionDeclaration:
        """Parses a function declaration."""
        name = self.consume("IDENTIFIER").value

        self.consume("LPAREN")
        parameters = []
        while self.peek().type != "RPAREN":
            parameters.append(self.consume("IDENTIFIER"))
            self.match("COMMA")
        self.consume("RPAREN")

        self.consume("LBRACE")
        body = []
        while self.peek().type != "RBRACE":
            body.append(self.statement())
        self.consume("RBRACE")
        return FunctionDeclaration(name, "VOID", parameters, body)

    def return_statement(self) -> ReturnStatement:
        """Parses a return statement."""
        value = self.expression()
        return ReturnStatement(value)

    def break_statement(self) -> BreakStatement:
        return BreakStatement()

    def function_call(self) -> FunctionCall:
        """Parses a function call."""
        name = self.consume("IDENTIFIER").value

        self.consume("LPAREN")
        arguments = []
        while self.peek().type != "RPAREN":
            # arguments.append(self.expression())
            arguments.append(self.consume("STRING"))
            self.match("COMMA")
        self.consume("RPAREN")
        return FunctionCall(name, arguments)

    def match_statement(self) -> MatchStatement:
        """Parses a match case."""
        self.consume("Match")
        value = self.consume("IDENTIFIER")

        self.consume("LBRACE")
        match_statements = []
        while self.peek().type != "ELSE" and self.peek().type != "RBRACE":
            value = self.expression()
            self.consume("ARROW")
            return_value = self.expression()
            match_statements.append(MatchCase(value, return_value))

        if self.match("ELSE"):
            self.consume("ARROW")
            match_statements.append(self.expression())

        self.consume("RBRACE")
        return MatchStatement(value, match_statements)

    ############################
    ## EXPRESSION PARSING
    ############################
    def range_expression(self) -> Range:
        """Parses a range expression."""
        start = self.consume("INT")
        self.consume("RANGE")
        end = self.consume("INT")
        return Range(start, end)

    def expression(self) -> Node:
        """Parses an expression with logical OR (`||`)."""
        return self.logical_or()

    def logical_or(self) -> BinaryOperation:
        """Parses logical OR (`||`) expressions."""
        left = self.logical_and()
        while self.match("OR"):
            operator = "||"
            right = self.logical_and()
            left = BinaryOperation(left, operator, right)
        return left

    def logical_and(self) -> BinaryOperation:
        """Parses logical AND (`&&`) expressions."""
        left = self.comparison()
        while self.match("AND"):
            operator = "&&"
            right = self.comparison()
            left = BinaryOperation(left, operator, right)
        return left

    def comparison(self) -> BinaryOperation:
        """Parses comparison expressions (`<`, `>`, `<=`, `>=`)."""
        left = self.equality()
        while self.match_set(("LESS_THAN", "LESS_EQUAL", "GREATER_THAN", "GREATER_EQUAL")):
            operator = self.tokens[self.current - 1].type
            right = self.equality()
            left = BinaryOperation(left, operator, right)
        return left

    def equality(self) -> BinaryOperation:
        """Parses equality expressions (`==`, `!=`)."""
        left = self.addition()
        while self.match("EQUAL_EQUAL", "BANG_EQUAL"):
            operator = self.tokens[self.current - 1].type
            right = self.addition()
            left = BinaryOperation(left, operator, right)
        return left

    def addition(self) -> BinaryOperation:
        """Parses expressions with '+' and '-'."""
        left = self.multiplication()
        while self.match("PLUS") or self.match("MINUS"):
            operator = self.tokens[self.current - 1].type
            right = self.multiplication()
            left = BinaryOperation(left, operator, right)
        return left

    def multiplication(self) -> BinaryOperation:
        """Parses expressions with '*' and '/'."""
        left = self.primary()
        while self.match("STAR") or self.match("SLASH"):
            operator = self.tokens[self.current - 1].type
            right = self.primary()
            left = BinaryOperation(left, operator, right)
        return left

    def primary(self) -> Token:
        """Parses literals (numbers and identifiers)."""
        if self.match("INT"):
            return self.tokens[self.current - 1]
        if self.match("FLOAT"):
            return self.tokens[self.current - 1]
        if self.match("IDENTIFIER"):
            return self.tokens[self.current - 1]
        raise SyntaxError("Expected a number or variable")
