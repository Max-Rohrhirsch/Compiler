from antlr4 import *

from Lexer import Lexer
from Parser import Parser
from SemanticAnalyzer import *
from CodeGenerator import CodeGenerator
from Lexer import Lexer



# java -jar Parser/antlr.jar -Dlanguage=Python3 -o Parser -visitor pym.g4

def parse():
    input_str = open("input.txt", "r").read()

    lexer = Lexer(input_str)
    tokens = lexer.build()
    print("Lexer:", tokens)

    parser = Parser(tokens)
    ast = parser.parse()
    print("Parser:", ast)

    analyzer = SemanticAnalyzer()
    o_ast = analyzer.analyze(ast)
    print("Semantic Analyzer:", o_ast)

    generator = CodeGenerator()
    generator.generate(o_ast)
    generator.dump()

if __name__ == '__main__':
    parse()