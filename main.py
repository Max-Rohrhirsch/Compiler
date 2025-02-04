from Lexer import Lexer
from Parser import Parser
from SemanticAnalyzer import SemanticAnalyzer
from CodeGenerator import CodeGenerator


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
    _llvm_ir = generator.generate(o_ast)
    assembly = generator.assembly
    print("CodeGenerator:", _llvm_ir)


if __name__ == '__main__':
    parse()
