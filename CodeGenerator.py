from logging.config import IDENTIFIER

from llvmlite import ir, binding

from SemanticAnalyzer import *


class CodeGenerator:
    def __init__(self):
        self.module = ir.Module(name="pym_module")
        self.builder = None
        self.function = None
        self.symbol_table = {}

    def generate(self, node):
        self.generate_main_function(node)

    def generate_main_function(self, node):
        func_type = ir.FunctionType(ir.VoidType(), [])
        self.function = ir.Function(self.module, func_type, name="main")
        block = self.function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        for stmt in node.statements:
            self.generate_statement(stmt)

        self.builder.ret_void()

    def generate_statement(self, node):
        if isinstance(node, VarDeclaration):
            value = self.generate_expression(node.value)
            self.symbol_table[node.name] = value
        elif isinstance(node, Assignment):
            if node.name not in self.symbol_table:
                raise Exception(f"Variable '{node.name}' not declared.")
            value = self.generate_expression(node.value)
            self.symbol_table[node.name] = value
        elif isinstance(node, BinaryOperation):
            return self.generate_expression(node)
        else:
            raise Exception(f"Unknown statement type: {type(node)}")

    def generate_expression(self, node):
        if isinstance(node, Token):
            return ir.Constant(ir.IntType(32), node.value)
        # elif isinstance(node, Identifier):
        #     if node.name not in self.symbol_table:
        #         raise Exception(f"Variable '{node.name}' not declared.")
        #     return self.symbol_table[node.name]
        elif isinstance(node, BinaryOperation):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)

            if node.operator == '+':
                return self.builder.add(left, right, name="addtmp")
            elif node.operator == '-':
                return self.builder.sub(left, right, name="subtmp")
            elif node.operator == '*':
                return self.builder.mul(left, right, name="multmp")
            elif node.operator == '/':
                return self.builder.sdiv(left, right, name="divtmp")
        else:
            raise Exception(f"Unknown expression type: {type(node)}")

    def dump(self):
        print(self.module)