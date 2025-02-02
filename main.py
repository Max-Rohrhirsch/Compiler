from antlr4 import *

from ASTBuilder import ASTBuilder
from Parser.pymLexer import pymLexer
from Parser.pymParser import pymParser
from SemanticAnalyzer import *
from CodeGenerator import CodeGenerator
from Lexer import Lexer



# java -jar Parser/antlr.jar -Dlanguage=Python3 -o Parser -visitor pym.g4

def parse():
    input_str = open("input.txt", "r").read()

    lexer = Lexer(input_str)
    tokens = lexer.build()
    print(tokens)
    # print("Lexer durch")
    #
    # parser = pymParser(stream)
    # tree = parser.program()
    # print("Tree wurde erstellt")
    # print(tree.toStringTree(recog=parser))

    # # print("fertig wirklich")
    # ast = Program([
    #     VarDeclaration("x", NumberLiteral(10)),
    #     Assignment("x", BinaryOperation(Variable("x"), '+', NumberLiteral(5)))
    # ])
    #
    # # 1. Semantische Analyse
    # analyzer = SemanticAnalyzer()
    # analyzer.analyze(ast)
    #
    # # 2. LLVM IR Code generieren
    # generator = CodeGenerator()
    # generator.generate(ast)
    # generator.dump()

if __name__ == '__main__':
    parse()