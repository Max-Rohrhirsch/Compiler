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

        # Type mappings
        self.type_map = {
            "INT": ir.IntType(32),
            "FLOAT": ir.FloatType(),
            "BOOL": ir.IntType(1),
            "CHAR": ir.IntType(8),
            # String will be handled as char pointers
            "STRING": ir.ArrayType(ir.IntType(8), 0).as_pointer(),
        }

        # RESULTS
        self.llvm_ir = ""
        self.assembly = ""

    def generate(self, node: list[Node,]) -> str:
        # SETUP LLVM
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        self.module.triple = binding.get_default_triple()

        # Add external functions like printf
        self.declare_external_functions()
        
        self.generate_main_function(node)

        self.llvm_ir = str(self.module)
        # print(self.llvm_ir)
        llvm_mod = binding.parse_assembly(self.llvm_ir)
        llvm_mod.verify()
        target = binding.Target.from_default_triple()
        machine = target.create_target_machine()
        self.assembly = machine.emit_assembly(llvm_mod)
        return self.llvm_ir

    def declare_external_functions(self):
        """Declare external C functions like printf"""
        # printf declaration
        printf_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")
        
        # malloc declaration
        malloc_ty = ir.FunctionType(ir.IntType(8).as_pointer(), [ir.IntType(64)])
        malloc = ir.Function(self.module, malloc_ty, name="malloc")
        
        # free declaration
        free_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(8).as_pointer()])
        free = ir.Function(self.module, free_ty, name="free")

    def generate_main_function(self, node: list[Node,]) -> None:
        func_type = ir.FunctionType(ir.IntType(32), [])
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
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self.generate_for_statement(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, UnaryOperation):
            self.generate_unary_operation(stmt)
        elif isinstance(stmt, FunctionCall):
            self.generate_function_call(stmt)
        elif isinstance(stmt, Comment):
            self.generate_comment(stmt.value)
        else:
            raise Exception(f"Unsupported statement type: {stmt}")

    def generate_comment(self, stmt: str) -> None:
        """ Adds a comment """
        pass  # LLVM IR doesn't support comments directly

    def generate_var_declaration(self, stmt: VarDeclaration) -> None:
        """ Creates a variable and stores it in the 'variables' map """
        data_type = stmt.data_type or self.infer_type(stmt.value)
        llvm_type = self.type_map.get(data_type, ir.IntType(32))
        
        ptr = self.builder.alloca(llvm_type, name=stmt.name)
        if stmt.value:
            value = self.generate_expression(stmt.value)
            # Convert if types don't match
            value = self.convert_type(value, data_type)
            self.builder.store(value, ptr)
        self.variables[stmt.name] = (ptr, data_type)

    def convert_type(self, value, target_type):
        """Converts a value to the target type if needed"""
        if value.type == self.type_map.get(target_type):
            return value
            
        # Int to float conversion
        if value.type == ir.IntType(32) and target_type == "FLOAT":
            return self.builder.sitofp(value, ir.FloatType())
            
        # Float to int conversion
        if value.type == ir.FloatType() and target_type == "INT":
            return self.builder.fptosi(value, ir.IntType(32))
            
        # Bool to int conversion
        if value.type == ir.IntType(1) and target_type == "INT":
            return self.builder.zext(value, ir.IntType(32))
            
        # Int to bool conversion
        if value.type == ir.IntType(32) and target_type == "BOOL":
            return self.builder.icmp_signed('!=', value, ir.Constant(ir.IntType(32), 0))
            
        return value  # Default to no conversion

    def infer_type(self, expr) -> str:
        """Infer the type of an expression"""
        if isinstance(expr, Token):
            return expr.type
        elif isinstance(expr, BinaryOperation):
            left_type = self.infer_type(expr.left)
            right_type = self.infer_type(expr.right)
            
            # Comparisons always result in a boolean
            if expr.operator in ("GREATER_THAN", "LESS_THAN", "EQUAL", "NOT_EQUAL", 
                                "GREATER_THAN_EQUAL", "LESS_THAN_EQUAL"):
                return "BOOL"
                
            # String concatenation
            if expr.operator == "PLUS" and (left_type == "STRING" or right_type == "STRING"):
                return "STRING"
                
            # Numeric operations result in float if any operand is float
            if left_type == "FLOAT" or right_type == "FLOAT":
                return "FLOAT"
                
            return "INT"  # Default to int for other operations
            
        return "INT"  # Default type

    def generate_assignment(self, stmt: Assignment) -> None:
        """ Sets an existing variable to a new value """
        if stmt.name not in self.variables:
            raise Exception(f"Variable {stmt.name} not declared!")
            
        ptr, var_type = self.variables[stmt.name]
        value = self.generate_expression(stmt.value)
        
        # Convert value to variable type if needed
        value = self.convert_type(value, var_type)
        self.builder.store(value, ptr)

    def generate_if_statement(self, stmt: IfStatement) -> None:
        """ Creates an If-Else structure """
        cond_val = self.generate_expression(stmt.condition)
        
        # Convert to boolean condition if needed
        if cond_val.type != ir.IntType(1):
            if cond_val.type == ir.FloatType():
                cond_bool = self.builder.fcmp_ordered('!=', cond_val, ir.Constant(ir.FloatType(), 0.0))
            else:
                cond_bool = self.builder.icmp_signed('!=', cond_val, ir.Constant(cond_val.type, 0))
        else:
            cond_bool = cond_val

        if_then = self.builder.append_basic_block("if_then")
        if_else = self.builder.append_basic_block("if_else") if stmt.else_body else None
        merge_block = self.builder.append_basic_block("merge")

        self.builder.cbranch(cond_bool, if_then, if_else if if_else else merge_block)

        # Generate the then block