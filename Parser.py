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

    def advance(self) -> Token:
        """Moves to the next token and returns it."""
        token = self.peek()
        self.current += 1
        return token

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

    def consume(self, expected_type: str, expected_value=None) -> Token:
        """Consume a token and move to the next. Optionally check its value."""
        token = self.peek()
        if token is None or token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but got {token.type if token else 'EOF'}")
        if expected_value is not None and token.value != expected_value:
            raise SyntaxError(f"Expected {expected_type} with value {expected_value}, but got {token.value}")
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
            return self.var_declaration("VAR")
        if self.match("KEYWORD", "CONST"):
            return self.var_declaration("CONST")
        if self.match("KEYWORD", "TEMP"):
            return self.var_declaration("TEMP")
        if self.match("KEYWORD", "POINTER"):
            return self.var_declaration("POINTER")
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
            elif self.peek() and self.peek().type == "DOT":
                self.current -= 1  # Go back to the identifier
                return self.property_assignment()
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
        if self.match("KEYWORD", "CLASS"):
            return self.class_declaration()
        if self.match("KEYWORD", "DATACLASS"):
            return self.dataclass_declaration()
        if self.match("KEYWORD", "MATCH"):
            return self.match_statement()
        if self.match("KEYWORD", "IMPORT"):
            return self.import_statement()
                
        raise SyntaxError(f"Invalid statement: {self.peek()}")
        
    def property_assignment(self) -> PropertyAssignment:
        """Parses: this.name = value;"""
        object_name = self.consume("IDENTIFIER").value
        self.consume("DOT")
        property_name = self.consume("IDENTIFIER").value
        self.consume("ASSIGN")
        value = self.expression()
        return PropertyAssignment(object_name, property_name, value)

    def var_declaration(self, var_type="VAR") -> VarDeclaration:
        """Parses: var [type] x = 10; or const int x = 5 or var int? x = null"""
        data_type = None
        nullable = False
        
        # Check for explicit data type
        if self.peek() and self.peek().type == "KEYWORD":
            data_type = self.advance().value
            
            # Check for nullability marker right after the type
            if self.peek() and self.peek().type == "NULLABLE":
                nullable = True
                self.advance()  # Consume '?'
        elif self.peek() and self.peek().type == "IDENTIFIER":
            # For custom types like i32, ui16, etc.
            type_token = self.peek()
            if type_token.value in ["i8", "i16", "i32", "i64", "ui8", "ui16", "ui32", "ui64", 
                                   "f32", "f64", "list", "dict", "array", "stack", "queue", "regex"]:
                data_type = self.advance().value
                
                # Check for nullability marker right after the type
                if self.peek() and self.peek().type == "NULLABLE":
                    nullable = True
                    self.advance()  # Consume '?'
        
        # Now expect the variable name identifier
        name = self.consume("IDENTIFIER").value
        
        self.consume("ASSIGN")
        value = self.expression()
        
        # Create the variable declaration with all details
        decl = VarDeclaration(name, value, data_type, var_type)
        decl.nullable = nullable
        
        return decl

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
        
        # Save the identifier name as an attribute
        attributes = [Attribute("name", identifier)]
        
        # Check for 'in' keyword
        if self.peek() and self.peek().type == "KEYWORD" and self.peek().value == "IN":
            self.advance()  # Consume 'in'
        else:
            # Support loops without 'in' keyword
            pass

        # Handle range expression: 1..5
        if self.peek() and self.peek().type == "INT":
            start_value = self.consume("INT")
            if self.peek() and self.peek().type == "RANGE":
                self.advance()  # Consume '..'
                end_value = self.consume("INT")
                value = Range(start_value, end_value, None)  # Third param is step (not used here)
            else:
                value = start_value  # Simple numeric iterator
        elif self.peek() and self.peek().type == "IDENTIFIER":
            value = self.consume("IDENTIFIER").value  # Iterating over a collection
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
        self.advance()  # Consume FUNCTION keyword
        
        # Check for optional return type
        return_type = "VOID"
        if self.peek() and self.peek().type == "KEYWORD":
            return_type = self.advance().value
            
        # Function name
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
        return FunctionDeclaration(name, return_type, parameters, body)

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
            arguments.append(self.null_coalescing())  # Use null_coalescing instead of expression directly
            while self.match("COMMA"):
                arguments.append(self.null_coalescing())  # Same here
        self.consume("RPAREN")
        return FunctionCall(name, arguments)

    def match_statement(self) -> MatchStatement:
        """Parses a match statement."""
        # The MATCH keyword was already consumed in the statement method
        self.consume("LPAREN")  # Consume the opening parenthesis
        value = self.expression()  # Parse the value to match against
        self.consume("RPAREN")  # Consume the closing parenthesis

        self.consume("LBRACE")
        cases = []
        
        # Process each case until we hit the closing brace or ELSE
        while self.peek() and self.peek().type != "RBRACE" and (self.peek().type != "KEYWORD" or self.peek().value != "ELSE"):
            case_value = self.expression()
            self.consume("ARROW")
            return_value = self.expression()
            cases.append(MatchCase(case_value, return_value))

        # Handle the optional ELSE case
        if self.peek() and self.peek().type == "KEYWORD" and self.peek().value == "ELSE":
            self.advance()  # Consume ELSE
            self.consume("ARROW")
            return_value = self.expression()
            cases.append(MatchCase(None, return_value))  # None means default case

        self.consume("RBRACE")
        return MatchStatement(value, cases)

    def class_declaration(self) -> ClassDeclaration:
        """Parses a class declaration."""
        name = self.consume("IDENTIFIER").value
        
        self.consume("LBRACE")
        methods = []
        properties = []
        constructor = None
        
        while self.peek() and self.peek().type != "RBRACE":
            if self.peek() and self.peek().type == "KEYWORD":
                if self.peek().value == "VAR":
                    # Handle variable declaration with the appropriate var_type
                    self.advance()  # Consume VAR
                    properties.append(self.var_declaration("VAR"))
                elif self.peek().value == "FUNCTION":
                    methods.append(self.function_declaration())
                elif self.peek().value == "CONSTRUCTOR":
                    constructor = self.constructor_declaration()
                else:
                    # Skip unknown keywords
                    self.advance()
            else:
                # Skip unknown class members
                self.advance()
        
        self.consume("RBRACE")
        return ClassDeclaration(name, properties, methods, constructor)

    def constructor_declaration(self) -> ConstructorDeclaration:
        """Parses a constructor declaration."""
        self.consume("KEYWORD", "CONSTRUCTOR")
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
        
        return ConstructorDeclaration(name, parameters, body)
        
    def dataclass_declaration(self) -> DataclassDeclaration:
        """Parses a dataclass declaration."""
        name = self.consume("IDENTIFIER").value
        
        self.consume("LPAREN")
        fields = []
        if self.peek() and self.peek().type != "RPAREN":
            # Parse fields with types
            data_type = None
            if self.peek() and self.peek().type == "KEYWORD":
                data_type = self.advance().value  # Get type
                
            field_name = self.consume("IDENTIFIER").value
            fields.append(DataclassField(field_name, data_type))
            
            while self.match("COMMA"):
                data_type = None
                if self.peek() and self.peek().type == "KEYWORD":
                    data_type = self.advance().value  # Get type
                    
                field_name = self.consume("IDENTIFIER").value
                fields.append(DataclassField(field_name, data_type))
                
        self.consume("RPAREN")
        
        return DataclassDeclaration(name, fields)
        
    def import_statement(self) -> ImportStatement:
        """Parses import statements."""
        target = None
        language = None
        
        # Check for language specifier in braces
        if self.peek() and self.peek().type == "LBRACE":
            self.consume("LBRACE")
            language = self.consume("IDENTIFIER").value
            self.consume("RBRACE")
        
        # Get the imported module/library name
        target = self.consume("IDENTIFIER").value
        
        return ImportStatement(target, language)

    ############################
    ## EXPRESSION PARSING
    ############################

    def expression(self) -> Node:
        """Parses an expression with logical OR (`||`)."""
        return self.null_coalescing()  # Add null coalescing as first step

    def null_coalescing(self) -> Node:
        """Parses null coalescing expressions with `??` operator."""
        left = self.logical_or()
        
        # Handle null coalescing operator
        while self.peek() and self.peek().type == "NULL_COALESCING":
            self.advance()  # Consume the ?? operator
            right = self.logical_or()
            left = BinaryOperation(left, "NULL_COALESCING", right)
            
        return left

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