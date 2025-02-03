from SemanticAnalyzer import *
from Lexer import Token
from llvmlite import ir, binding


class CodeGenerator:
    def __init__(self):
        # Initialize the LLVM binding and target.
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # Create a new LLVM module.
        self.module = ir.Module(name="pym_module")
        self.builder = None
        self.function = None
        self.symbol_table = {}  # maps variable names to alloca instructions

    def generate(self, node):
        # The top-level node is expected to be a list of statements.
        self.generate_main_function(node)

    def generate_main_function(self, node):
        # Create the main function signature: void main()
        func_type = ir.FunctionType(ir.VoidType(), [])
        self.function = ir.Function(self.module, func_type, name="main")
        block = self.function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        for stmt in node:
            self.generate_statement(stmt)

        self.builder.ret_void()

    def generate_statement(self, stmt):
        # Dispatch based on the type of the statement.
        if stmt.__class__.__name__ == "VarDeclaration":
            self.generate_var_declaration(stmt)
        elif stmt.__class__.__name__ == "IfStatement":
            self.generate_if_statement(stmt)
        else:
            raise Exception(f"Unsupported statement type: {stmt}")

    def generate_var_declaration(self, stmt):
        # Assuming stmt has attributes: type, identifier, and initializer.
        # Here, we handle integer variables as an example.
        var_name = stmt.identifier.value  # adjust based on your AST structure
        var_type = ir.IntType(32)  # assuming an INT type
        # Allocate space on the stack for the variable.
        alloc = self.builder.alloca(var_type, name=var_name)
        self.symbol_table[var_name] = alloc

        # If there is an initializer, generate its value.
        if stmt.initializer is not None:
            init_val = self.generate_expression(stmt.initializer)
            self.builder.store(init_val, alloc)

    def generate_if_statement(self, stmt):
        # Generate the condition expression; expect an i1 (boolean) result.
        cond_val = self.generate_expression(stmt.condition)
        # Create basic blocks for the then and merge (and else if needed).
        then_bb = self.function.append_basic_block(name="if_then")
        merge_bb = self.function.append_basic_block(name="if_merge")

        if stmt.else_body is not None:
            else_bb = self.function.append_basic_block(name="if_else")
            self.builder.cbranch(cond_val, then_bb, else_bb)
        else:
            self.builder.cbranch(cond_val, then_bb, merge_bb)

        # Emit code for the then block.
        self.builder.position_at_start(then_bb)
        for then_stmt in stmt.then_body:
            self.generate_statement(then_stmt)
        # Branch to merge after then.
        if self.builder.block.terminator is None:
            self.builder.branch(merge_bb)

        # Else block, if present.
        if stmt.else_body is not None:
            self.builder.position_at_start(else_bb)
            for else_stmt in stmt.else_body:
                self.generate_statement(else_stmt)
            if self.builder.block.terminator is None:
                self.builder.branch(merge_bb)

        # Position the builder at the merge block.
        self.builder.position_at_start(merge_bb)

    def generate_expression(self, expr):
        # Dispatch based on the type of expression.
        if expr.__class__.__name__ == "BinaryOperation":
            return self.generate_binary_operation(expr)
        elif expr.__class__.__name__ == "Identifier":
            return self.generate_identifier(expr)
        elif expr.__class__.__name__ == "IntLiteral":
            return ir.Constant(ir.IntType(32), int(expr.value))
        # Add more expression types as needed.
        else:
            raise Exception(f"Unsupported expression type: {expr}")

    def generate_binary_operation(self, expr):
        # Generate the left and right operands.
        left = self.generate_expression(expr.left)
        right = self.generate_expression(expr.right)

        # Dispatch based on the operator.
        if expr.operator == "PLUS":
            return self.builder.add(left, right, name="addtmp")
        elif expr.operator == "GREATER_THAN":
            # For signed integers, use icmp_signed; the result is i1.
            cmp = self.builder.icmp_signed(">", left, right, name="cmptmp")
            # Depending on your language semantics, you might need to convert i1 to i32.
            # For example, if a boolean is represented as an integer:
            return self.builder.zext(cmp, ir.IntType(32), name="booltmp")
        # Handle additional operators like MINUS, TIMES, etc.
        else:
            raise Exception(f"Unsupported binary operator: {expr.operator}")

    def generate_identifier(self, expr):
        # Look up the variable in the symbol table.
        var_name = expr.value  # adjust based on your AST
        alloc = self.symbol_table.get(var_name)
        if alloc is None:
            raise Exception(f"Undefined variable: {var_name}")
        return self.builder.load(alloc, name=var_name + "_val")

    def dump(self):
        print(self.module)