from Nodes import Token

############################
## CONSTANTS
############################

Keywords = [
    "IF",
    "ELSE",
    "WHILE",
    "FOR",
    "IN",
    "BREAK",
    "CONTINUE",
    "RETURN",
    "FUNCTION",
    "MATCH",

    "VAR",
    "CONST",
    "TEMP",
    "POINTER",

    "TRUE",
    "FALSE",

    "CLASS",
    "DATACLASS",
    "ENUM",
    "CONSTRUCTOR",
    "DESTRUCTOR",

    "IMPORT",
    "INCLUDE",
    "FROM",
    
    # Data types
    "INT",
    "FLOAT",
    "STRING",
    "BOOL",
    "CHAR",
    "VOID"
]

Operators = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MUL",
    "/": "DIV",
    "%": "MOD",
    "**": "POW",  # Exponentiation

    "=": "ASSIGN",
    "+=": "PLUS_ASSIGN",
    "-=": "MINUS_ASSIGN",
    "*=": "MUL_ASSIGN",
    "/=": "DIV_ASSIGN",
    "%=": "MOD_ASSIGN",
    "**=": "POW_ASSIGN",

    "==": "EQUAL",
    "!=": "NOT_EQUAL",
    "<": "LESS_THAN",
    ">": "GREATER_THAN",
    "<=": "LESS_THAN_EQUAL",
    ">=": "GREATER_THAN_EQUAL",
    "&&": "AND",
    "||": "OR",
    "!": "NOT",

    "..": "RANGE",
    "->": "ARROW",
    "=>": "FAT_ARROW",

    "++": "INCREMENT",
    "--": "DECREMENT",
    "!!": "NEGATE",

    ">>": "RIGHT_SHIFT",
    "<<": "LEFT_SHIFT",
    "&": "BITWISE_AND",
    "|": "BITWISE_OR",
    "^": "BITWISE_XOR",
    "~": "BITWISE_NOT",
    "??": "NULL_COALESCING",
    "??=": "NULL_COALESCING_ASSIGN",
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
    "?": "NULLABLE",  # Added nullable type marker
}


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
        while self.current_char is not None:
            if self.current_char.isalpha() or self.current_char == "_":
                self._make_identifier()
            elif self.current_char.isdigit():
                self._make_number()
            elif self.current_char in "\"'":
                self._make_string()
            elif self.current_char == "/" and self.pos + 1 < len(self.input) and self.input[self.pos + 1] == "/":
                self._make_comment()
            elif self.current_char == "#":
                self._make_comment()
            elif self.current_char == "." and self.pos + 1 < len(self.input) and self.input[self.pos + 1] == ".":
                # Handle range operator ".."
                self._add_token("RANGE", None)
                self._next_token(False)  # Skip first dot
                self._next_token()       # Skip second dot
            elif self.current_char == "?" and self.pos + 1 < len(self.input) and self.input[self.pos + 1] == "?":
                # Handle null coalescing operator "??"
                self._add_token("NULL_COALESCING", None)
                self._next_token(False)  # Skip first question mark
                self._next_token()       # Skip second question mark
            elif self.current_char in Operators:
                operator = self.current_char
                self._next_token(False)
                if self.current_char is not None and operator + self.current_char in Operators:
                    operator += self.current_char
                    self._next_token(False)
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
    def _make_comment(self) -> None:
        comment = ""
        self._next_token(False)
        while self.current_char is not None and self.current_char != "\n":
            comment += self.current_char
            self._next_token(False)
        self._add_token("COMMENT", comment)

    def _make_identifier(self) -> None:
        identifier = ""
        last_line: int = self.line
        last_column: int = self.column

        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == "_"):
            identifier += self.current_char
            self._next_token(False)
            
        if identifier.upper() in Keywords:
            if identifier.upper() == "TRUE":
                self._add_token("BOOL", True, last_line, last_column)
            elif identifier.upper() == "FALSE":
                self._add_token("BOOL", False, last_line, last_column)
            else:
                self._add_token("KEYWORD", identifier.upper(), last_line, last_column)
        else:
            self._add_token("IDENTIFIER", identifier, last_line, last_column)

    def _make_string(self) -> None:
        string = ""
        string_char = self.current_char
        last_line: int = self.line
        last_column: int = self.column
        
        self._next_token(False)  # Skip opening quote
        
        while self.current_char is not None and self.current_char != string_char:
            if self.current_char == "\\":
                self._next_token(False)
                if self.current_char == "n":
                    string += "\n"
                elif self.current_char == "t":
                    string += "\t"
                elif self.current_char == "r":
                    string += "\r"
                elif self.current_char == "\\":
                    string += "\\"
                elif self.current_char == string_char:
                    string += string_char
                else:
                    string += self.current_char
            else:
                string += self.current_char
            self._next_token(False)
            
        if self.current_char is None:
            self._error("Unterminated string")
            
        self._next_token(False)  # Skip closing quote
        
        if len(string) == 1:
            self._add_token("CHAR", string, last_line, last_column)
        else:
            self._add_token("STRING", string, last_line, last_column)

    def _make_number(self) -> None:
        number = ""
        is_float = False
        last_line: int = self.line
        last_column: int = self.column
        
        # Process integer part
        while self.current_char is not None and self.current_char.isdigit():
            number += self.current_char
            self._next_token(False)
        
        # Check for decimal point (but not range operator)
        if (self.current_char == '.' and 
            (self.pos + 1 >= len(self.input) or 
             self.input[self.pos + 1] != '.')):
            
            is_float = True
            number += self.current_char
            self._next_token(False)
            
            # Process decimal part
            while self.current_char is not None and self.current_char.isdigit():
                number += self.current_char
                self._next_token(False)
        
        # Create the appropriate token
        if is_float:
            self._add_token("FLOAT", float(number), last_line, last_column)
        else:
            self._add_token("INT", int(number), last_line, last_column)