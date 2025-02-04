from SemanticAnalyzer import *
from Lexer import Token
from llvmlite import ir, binding


class CodeGenerator:
    def __init__(self) -> None:
        # Create a new LLVM module.
        self.module = ir.Module(name="pym_module")
        self.builder = None
        self.function = None
        self.symbol_table = {}

        # RESULTS
        self.llvm_ir = ""
        self.assembly = ""

    def generate(self, node: list[Node,]) -> str:
        # SETUP LLVM
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        self.module.triple = binding.get_default_triple()

        self.generate_main_function(node)

        self.llvm_ir = str(self.module)
        llvm_mod = binding.parse_assembly(self.llvm_ir)
        llvm_mod.verify()
        target = binding.Target.from_default_triple()
        machine = target.create_target_machine()
        self.assembly = machine.emit_assembly(llvm_mod)
        return self.llvm_ir

    def generate_main_function(self, node: list[Node,]) -> None:
        # Create the main function signature: void main()
        func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        function = ir.Function(self.module, func_type, name="main")
        block = function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        for stmt in node:
            self.generate_statement(stmt)

        self.builder.ret_void()

    def generate_statement(self, stmt: Node) -> None:
        # Dispatch based on the type of the statement.
        if isinstance(stmt, VarDeclaration):
            self.generate_var_declaration(stmt)
        elif stmt.__class__.__name__ == "IfStatement":
            self.generate_if_statement(stmt)
        else:
            raise Exception(f"Unsupported statement type: {stmt}")

    def generate_var_declaration(self, stmt: VarDeclaration) -> None:
        ...

    def generate_if_statement(self, stmt: IfStatement) -> None:
        ...

    def generate_expression(self, expr: BinaryOperation) -> None:
        ...

    def generate_binary_operation(self, expr: BinaryOperation) -> None:
        left = self.generate_expression(expr.left)
        right = self.generate_expression(expr.right)

        if expr.operator == "PLUS":
            return self.builder.add(left, right, name="addtmp")
        elif expr.operator == "GREATER_THAN":
            cmp = self.builder.icmp_signed(">", left, right, name="cmptmp")
            return self.builder.zext(cmp, ir.IntType(32), name="booltmp")
        else:
            raise Exception(f"Unsupported binary operator: {expr.operator}")
