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
    def __init__(self, _type, value, line, column) -> None:
        self.type = _type
        self.value = value
        self.line = line
        self.column = column
        self.current_token = None

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"


############################
## Lexer Class
############################

class Lexer:
    def __init__(self, input_str: str) -> None:
        self.input = input_str
        self.pos = -1
        self.line = 1
        self.column = -1
        self.current_char = None
        self.tokens = []

    def _next_token(self, skip_whitespace=True) -> None:
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

    def _error(self, message) -> None:
        raise Exception(f"Lexer error: {message} at line {self.line}, column {self.column}")

    def _add_token(self, token, value, line=-1, column=-1) -> None:
        if line == -1:
            line = self.line
        if column == -1:
            column = self.column
        self.tokens.append(Token(token, value, line, column))


    ############################
    ## MAIN FUNCTION
    ############################

    def build(self) -> list[Token]:
        self._next_token()
        while self.current_char is not None :
            if self.current_char.isalpha() or self.current_char == "_":
                self._make_identifier()
            elif self.current_char.isdigit():
                self._make_number()
            elif self.current_char in "\"'":
                self._make_string()
            elif self.current_char in Operators:
                operator = self.current_char
                self._next_token()
                if self.current_char in Operators:
                    operator += self.current_char
                    self._next_token()
                self._add_token(Operators[operator], None)
            elif self.current_char in Symbols:
                self._add_token(Symbols[self.current_char], None)
                self._next_token()
            elif self.current_char in " \t\n":
                self._next_token()
            else:
                self._error(f"Invalid character '{self.current_char}'")
        self._add_token("EOF", None)
        return self.tokens


    ############################
    ## MAKE FUNCTIONS
    ############################

    def _make_identifier(self) -> None:
        identifier = ""
        last_line: int = self.line
        last_column: int = self.column

        while self.current_char.isalpha() or self.current_char == "_":
            identifier += self.current_char
            self._next_token(False)
        if identifier.upper() in Keywords:
            self._add_token("KEYWORD", identifier.upper(), last_line, last_column)
        else:
            self._add_token("IDENTIFIER", identifier, last_line, last_column)

    def _make_string(self) -> None:
        string = ""
        string_char = self.current_char

        while self.current_char != string_char:
            if self.current_char == "\\":
                self._next_token()
                if self.current_char == "n":
                    string += "\n"
                elif self.current_char == "t":
                    string += "\t"
                else:
                    string += self.current_char
            string += self.current_char
            self._next_token()

    def _make_number(self) -> None:
        number = ""
        is_float = False
        while self.current_char in "0123456789._":
            if self.current_char == ".":
                is_float = True
                self._next_token(False)
            elif self.current_char == "_":
                self._next_token(False)
            else:
                number += self.current_char
                self._next_token(False)
        if is_float:
            self._add_token("FLOAT", float(number))
        else:
            self._add_token("INT", int(number))