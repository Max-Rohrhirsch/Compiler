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

    def peek(self) -> Token:
        """Returns the current token without consuming it."""
        return self.tokens[self.current] if self.current < len(self.tokens) else None

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

    ############################
    ## MAIN FUNCTION
    ############################

    def parse(self) -> list[Node]:
        """Entry point for parsing: Parses a full program."""
        statements = []
        while self.peek() and self.peek().type != "EOF":
            statements.append(self.statement())
        return statements

    ############################
    ## MAKER FUNCTIONS
    ############################

    def statement(self) -> Node:
        """Parses statements like variable declarations and assignments."""
        print("Parsing statement", self.peek())
        if self.match("KEYWORD", "VAR"):
            return self.var_declaration()
        if self.match("IDENTIFIER"):
            token_value = self.tokens[self.current - 1].value
            # Check next token to determine if it's a function call, assignment or increment/decrement
            if self.peek() and self.peek().type == "LPAREN":
                self.current -= 1  # Go back to the identifier
                return self.function_call()
            elif self.peek() and self.peek().type == "INCREMENT":
                self.advance()  # Consume ++
                return UnaryOperation("INCREMENT", token_value)
            elif self.peek() and self.peek().type == "DECREMENT":
                self.advance()  # Consume --
                return UnaryOperation("DECREMENT", token_value)
            else:
                self.current -= 1  # Go back to the identifier
                return self.assignment()
        if self.match("KEYWORD", "IF"):
            return self.if_statement()
        if self.peek() and self.peek().type == "COMMENT":
            return Comment(self.consume("COMMENT").value)
        if self.match("KEYWORD", "WHILE"):
            return self.while_statement()
        if self.match("KEYWORD", "FOR"):
            return self.for_statement()
        if self.match("KEYWORD", "FUNCTION"):
            return self.function_declaration()
        if self.match("KEYWORD", "BREAK"):
            return self.break_statement()
        if self.match("KEYWORD", "RETURN"):
            return self.return_statement()
                
        raise SyntaxError(f"Invalid statement: {self.peek()}")

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
        # Check if there are parentheses (optional in this language)
        has_parens = False
        if self.peek() and self.peek().type == "LPAREN":
            self.consume("LPAREN")
            has_parens = True
            
        condition = self.expression()
        
        if has_parens:
            self.consume("RPAREN")

        self.consume("LBRACE")
        then_body = []
        while self.peek() and self.peek().type != "RBRACE":
            then_body.append(self.statement())
        self.consume("RBRACE")

        else_body = None
        if self.peek() and self.peek().type == "KEYWORD" and self.peek().value == "ELSE":
            self.advance()  # Consume ELSE
            self.consume("LBRACE")
            else_body = []
            while self.peek() and self.peek().type != "RBRACE":
                else_body.append(self.statement())
            self.consume("RBRACE")

        return IfStatement(condition, then_body, else_body)

    def while_statement(self) -> WhileStatement:
        """Parses a while-statement into an AST node."""
        # Check if there are parentheses (optional in this language)
        has_parens = False
        if self.peek() and self.peek().type == "LPAREN":
            self.consume("LPAREN")
            has_parens = True
            
        condition = self.expression()
        
        if has_parens:
            self.consume("RPAREN")

        self.consume("LBRACE")
        body = []
        while self.peek() and self.peek().type != "RBRACE":
            body.append(self.statement())
        self.consume("RBRACE")
        return WhileStatement(condition, body)

    def for_statement(self) -> ForStatement:
        """Parses a for-statement into an AST node."""
        identifier = self.consume("IDENTIFIER").value
        
        # Save the identifier name
        attributes = [identifier]
        
        # Check for comma-separated identifiers
        while self.match("COMMA"):
            attributes.append(self.consume("IDENTIFIER").value)

        # Check for 'in' keyword
        if self.peek() and self.peek().type == "KEYWORD" and self.peek().value == "IN":
            self.advance()  # Consume 'in'
        else:
            # Support loops without 'in' keyword
            pass

        # Get the value to iterate over
        if self.peek() and self.peek().type == "INT":
            value = self.consume("INT").value
        elif self.peek() and self.peek().type == "IDENTIFIER":
            value = self.consume("IDENTIFIER").value
        else:
            # Try as an expression
            value = self.expression()

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
        if self.peek() and self.peek().type != "RPAREN":
            parameters.append(self.consume("IDENTIFIER").value)
            while self.match("COMMA"):
                parameters.append(self.consume("IDENTIFIER").value)
        self.consume("RPAREN")

        self.consume("LBRACE")
        body = []
        while self.peek() and self.peek().type != "RBRACE":
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
        if self.peek() and self.peek().type != "RPAREN":
            arguments.append(self.expression())
            while self.match("COMMA"):
                arguments.append(self.expression())
        self.consume("RPAREN")
        return FunctionCall(name, arguments)

    def match_statement(self) -> MatchStatement:
        """Parses a match case."""
        self.consume("KEYWORD", "MATCH")
        value = self.consume("IDENTIFIER").value

        self.consume("LBRACE")
        match_statements = []
        while self.peek() and (self.peek().type != "KEYWORD" or self.peek().value != "ELSE") and self.peek().type != "RBRACE":
            case_value = self.expression()
            self.consume("ARROW")
            return_value = self.expression()
            match_statements.append(MatchCase(case_value, return_value))

        if self.match("KEYWORD", "ELSE"):
            self.consume("ARROW")
            match_statements.append(MatchCase(None, self.expression()))

        self.consume("RBRACE")
        return MatchStatement(value, match_statements)

    ############################
    ## EXPRESSION PARSING
    ############################

    def expression(self) -> Node:
        """Parses an expression with logical OR (`||`)."""
        return self.logical_or()

    def logical_or(self) -> Node:
        """Parses logical OR (`||`) expressions."""
        left = self.logical_and()
        while self.peek() and self.peek().type == "OR":
            operator = self.consume("OR").type
            right = self.logical_and()
            left = BinaryOperation(left, operator, right)
        return left

    def logical_and(self) -> Node:
        """Parses logical AND (`&&`) expressions."""
        left = self.equality()
        while self.peek() and self.peek().type == "AND":
            operator = self.consume("AND").type
            right = self.equality()
            left = BinaryOperation(left, operator, right)
        return left

    def equality(self) -> Node:
        """Parses equality expressions (`==`, `!=`)."""
        left = self.comparison()
        while self.peek() and (self.peek().type == "EQUAL" or self.peek().type == "NOT_EQUAL"):
            operator = self.consume(self.peek().type).type
            right = self.comparison()
            left = BinaryOperation(left, operator, right)
        return left

    def comparison(self) -> Node:
        """Parses comparison expressions (`<`, `>`, `<=`, `>=`)."""
        left = self.addition()
        while self.peek() and self.peek().type in ("LESS_THAN", "LESS_THAN_EQUAL", "GREATER_THAN", "GREATER_THAN_EQUAL"):
            operator = self.consume(self.peek().type).type
            right = self.addition()
            left = BinaryOperation(left, operator, right)
        return left

    def addition(self) -> Node:
        """Parses expressions with '+' and '-'."""
        left = self.multiplication()
        while self.peek() and (self.peek().type == "PLUS" or self.peek().type == "MINUS"):
            operator = self.consume(self.peek().type).type
            right = self.multiplication()
            left = BinaryOperation(left, operator, right)
        return left

    def multiplication(self) -> Node:
        """Parses expressions with '*' and '/'."""
        left = self.primary()
        while self.peek() and (self.peek().type == "MUL" or self.peek().type == "DIV" or self.peek().type == "MOD"):
            operator = self.consume(self.peek().type).type
            right = self.primary()
            left = BinaryOperation(left, operator, right)
        return left

    def primary(self) -> Node:
        """Parses literals (numbers and identifiers)."""
        if self.peek() and self.peek().type == "INT":
            return self.consume("INT")
        if self.peek() and self.peek().type == "FLOAT":
            return self.consume("FLOAT")
        if self.peek() and self.peek().type == "IDENTIFIER":
            token = self.consume("IDENTIFIER")
            # Check if it's a function call
            if self.peek() and self.peek().type == "LPAREN":
                self.current -= 1  # Go back to the identifier
                return self.function_call()
            return token
        if self.peek() and self.peek().type == "LPAREN":
            self.consume("LPAREN")
            expr = self.expression()
            self.consume("RPAREN")
            return expr
        if self.peek() and self.peek().type == "STRING":
            return self.consume("STRING")
        if self.peek() and self.peek().type == "BOOL":
            return self.consume("BOOL")
            
        raise SyntaxError(f"Expected a primary expression, got {self.peek() and self.peek().type}")