program: statement* EOF -> ^(PROGRAM statement*);

statement
    : varDeclaration -> ^(VAR_DECL varDeclaration)
    | assignmentStatement -> ^(ASSIGN assignmentStatement)
    | ifStatement -> ^(IF_STATEMENT ifStatement)
    | expressionStatement -> ^(EXPR_STMT expressionStatement)
    ;

varDeclaration
    : 'var' IDENTIFIER '=' expression ';' -> ^(VAR_DECL IDENTIFIER expression);

assignmentStatement
    : IDENTIFIER '=' expression ';' -> ^(ASSIGN IDENTIFIER expression);

ifStatement
    : 'if' '(' expression ')' '{' statement* '}'
      ('else' '{' statement* '}')? 
      -> ^(IF expression statement* (ELSE statement*)?);

expression
    : '(' expression ')' -> expression
    | expression op=('*'|'/') expression -> ^(MUL_DIV expression expression)
    | expression op=('+'|'-') expression -> ^(ADD_SUB expression expression)
    | expression op=('<'|'>'|'<='|'>=') expression -> ^(COMP expression expression)
    | expression op=('=='|'!=') expression -> ^(EQUALITY expression expression)
    | expression '&&' expression -> ^(AND expression expression)
    | expression '||' expression -> ^(OR expression expression)
    | primary -> primary
    ;

primary
    : NUMBER -> ^(NUMBER NUMBER)
    | STRING -> ^(STRING STRING)
    | BOOLEAN -> ^(BOOLEAN BOOLEAN)
    | IDENTIFIER -> ^(VAR IDENTIFIER)
    ;

NUMBER: [0-9]+ ('.' [0-9]+)?;
STRING: '"' .*? '"';
BOOLEAN: 'true' | 'false';
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

WS: [ \t\r\n]+ -> skip;
COMMENT: '//' .*? '\r'? '\n' -> skip;
