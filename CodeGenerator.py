from SemanticAnalyzer import *
from llvmlite import ir, binding
from Lexer import Operators


class CodeGenerator:
    def __init__(self) -> None:
        # Create a new LLVM module.
        self.module = ir.Module(name="pym_module")
        self.builder = None
        self.function = None
        self.variables = {}

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
        # print(self.llvm_ir)
        llvm_mod = binding.parse_assembly(self.llvm_ir)
        llvm_mod.verify()
        target = binding.Target.from_default_triple()
        machine = target.create_target_machine()
        self.assembly = machine.emit_assembly(llvm_mod)
        return self.llvm_ir

    def generate_main_function(self, node: list[Node,]) -> None:
        func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        function = ir.Function(self.module, func_type, name="main")
        block = function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        for stmt in node:
            self.generate_statement(stmt)

        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    def generate_statement(self, stmt: Node) -> None:
        if isinstance(stmt, VarDeclaration):
            self.generate_var_declaration(stmt)
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, Comment):
            self.generate_comment(stmt.value)
        else:
            raise Exception(f"Unsupported statement type: {stmt}")

    def generate_comment(self, stmt: str) -> None:
        """ Fügt einen Kommentar hinzu """
        self.builder.comment(stmt)

    def generate_var_declaration(self, stmt: VarDeclaration) -> None:
        """ Erstellt eine Variable und speichert sie in der 'variables'-Map """
        ptr = self.builder.alloca(ir.IntType(32), name=stmt.name)
        if stmt.value:
            value = self.generate_expression(stmt.value)
            self.builder.store(value, ptr)
        self.variables[stmt.name] = ptr

    def generate_assignment(self, stmt: Assignment) -> None:
        """ Setzt eine bestehende Variable auf einen neuen Wert """
        if stmt.name not in self.variables:
            raise Exception(f"Variable {stmt.name} not declared!")
        value = self.generate_expression(stmt.value)
        self.builder.store(value, self.variables[stmt.name])

    def generate_if_statement(self, stmt: IfStatement) -> None:
        """ Erstellt eine If-Else-Struktur """
        cond_val = self.generate_expression(stmt.condition)
        cond_bool = self.builder.icmp_signed('!=', cond_val, ir.Constant(ir.IntType(32), 0))

        if_then = self.builder.append_basic_block("if_then")
        if_else = self.builder.append_basic_block("if_else") if stmt.else_body else None
        merge_block = self.builder.append_basic_block("merge")

        self.builder.cbranch(cond_bool, if_then, if_else if if_else else merge_block)

        # If-Block generieren
        self.builder.position_at_end(if_then)
        for sub_stmt in stmt.then_body:
            self.generate_statement(sub_stmt)
        self.builder.branch(merge_block)

        # Else-Block (falls vorhanden)
        if if_else:
            self.builder.position_at_end(if_else)
            for sub_stmt in stmt.else_body:
                self.generate_statement(sub_stmt)
            self.builder.branch(merge_block)

        self.builder.position_at_end(merge_block)

    def generate_expression(self, expr) -> ir.Value:
        """Generiert einen Wert oder eine binäre Operation."""
        if isinstance(expr, BinaryOperation):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)

            if expr.operator == Operators["+"]:
                return self.builder.add(left, right)
            elif expr.operator == Operators["-"]:
                return self.builder.sub(left, right)
            elif expr.operator == Operators["*"]:
                return self.builder.mul(left, right)
            elif expr.operator == Operators["/"]:
                return self.builder.sdiv(left, right)
            elif expr.operator == Operators["<"]:
                return self.builder.icmp_signed('<', left, right)
            elif expr.operator == Operators[">"]:
                return self.builder.icmp_signed('>', left, right)
            elif expr.operator == Operators["=="]:
                return self.builder.icmp_signed('==', left, right)
            elif expr.operator == Operators["!="]:
                return self.builder.icmp_signed('!=', left, right)
            else:
                raise Exception(f"Unsupported operator {expr.operator}")

        elif isinstance(expr, Token):
            if expr.type == "INT":
                return ir.Constant(ir.IntType(32), int(expr.value))
            elif expr.type == "FLOAT":
                return ir.Constant(ir.FloatType(), float(expr.value))
            elif expr.type == "IDENTIFIER":
                if expr.value in self.variables:
                    return self.builder.load(self.variables[expr.value])
                else:
                    raise Exception(f"Undefined variable: {expr.value}")

            else:
                raise Exception(f"Unsupported token type {expr.type}")

        elif isinstance(expr, str) and expr in self.variables:
            return self.builder.load(self.variables[expr])

        else:
            raise Exception(f"Unknown expression type: {expr}")

    def get_value(self, val):
        """ Wandelt einen Wert um (Konstante oder Variable) """
        if isinstance(val, int):
            return ir.Constant(ir.IntType(32), val)
        elif isinstance(val, str) and val in self.variables:
            return self.builder.load(self.variables[val])
        else:
            raise Exception(f"Unknown value: {val}")
