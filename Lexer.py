############################
## CONSTANTS
############################

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


############################
## Token Class
############################

class Token:
    def __init__(self, _type, value, line, column):
        self.type = _type
        self.value = value
        self.line = line
        self.column = column
        self.current_token = None

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"


############################
## Lexer Class
############################

class Lexer:
    def __init__(self, input_str: str):
        self.input = input_str
        self.pos = -1
        self.line = 1
        self.column = -1
        self.current_char = None
        self.tokens = []

    def next_token(self, skip_whitespace=True):
        print(f"start {self.current_char = }, {self.pos = }, {self.line = }, {self.column = }")
        self.pos += 1

        # Handle any leading whitespace and newlines
        if skip_whitespace:
            while self.pos < len(self.input) and self.input[self.pos] in " \t\n":
                if self.input[self.pos] == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

        if self.pos >= len(self.input):
            self.current_char = None
            return

        self.current_char = self.input[self.pos]

        self.column += 1

        print(f"end   {self.current_char = }, {self.pos = }, {self.line = }, {self.column = }")

    def error(self, message):
        raise Exception(f"Lexer error: {message} at line {self.line}, column {self.column}")

    def add_token(self, token, value, line=-1, column=-1):
        if line == -1:
            line = self.line
        if column == -1:
            column = self.column
        self.tokens.append(Token(token, value, line, column))


    ############################
    ## MAIN FUNCTION
    ############################

    def build(self):
        self.next_token()
        while self.current_char is not None :
            if self.current_char.isalpha() or self.current_char == "_":
                self.make_identifier()
            elif self.current_char.isdigit():
                self.make_number()
            elif self.current_char in "\"'":
                self.make_string()
            elif self.current_char in Operators:
                operator = self.current_char
                self.next_token()
                if self.current_char in Operators:
                    operator += self.current_char
                    self.next_token()
                self.add_token(Operators[operator], None)
            elif self.current_char in Symbols:
                self.add_token(Symbols[self.current_char], None)
                self.next_token()
            elif self.current_char in " \t\n":
                self.next_token()
            else:
                self.error(f"Invalid character '{self.current_char}'")
        self.add_token("EOF", None)
        return self.tokens


    ############################
    ## MAKE FUNCTIONS
    ############################

    def make_identifier(self):
        identifier = ""
        last_line: int = self.line
        last_column: int = self.column

        while self.current_char.isalpha() or self.current_char == "_":
            identifier += self.current_char
            self.next_token(False)
        if identifier.upper() in Keywords:
            self.add_token("KEYWORD", identifier.upper(), last_line, last_column)
        else:
            self.add_token("IDENTIFIER", identifier, last_line, last_column)

    def make_string(self):
        string = ""
        string_char = self.current_char

        while self.current_char != string_char:
            if self.current_char == "\\":
                self.next_token()
                if self.current_char == "n":
                    string += "\n"
                elif self.current_char == "t":
                    string += "\t"
                else:
                    string += self.current_char
            string += self.current_char
            self.next_token()

    def make_number(self):
        number = ""
        is_float = False
        while self.current_char in "0123456789._":
            if self.current_char == ".":
                is_float = True
                self.next_token(False)
            elif self.current_char == "_":
                self.next_token(False)
            else:
                number += self.current_char
                self.next_token(False)
        if is_float:
            self.add_token("FLOAT", float(number))
        else:
            self.add_token("INT", int(number))