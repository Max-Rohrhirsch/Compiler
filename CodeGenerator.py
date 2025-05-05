from SemanticAnalyzer import *
from llvmlite import ir, binding
from Lexer import Operators


class CodeGenerator:
    def __init__(self, source_file_name='input'):
        """Initialize LLVM code generator"""
        # Set up LLVM module and builder
        self.module = ir.Module(name=source_file_name)
        self.builder = None
        self.function = None
        
        # Create a mapping of variable names to their values
        self.variables = {}
        
        # Store custom types
        self.types = {}
        
        # Counter for temporary variables and blocks
        self.temp_counter = 0
        
        # Create type declarations
        self.void_type = ir.VoidType()
        self.int_type = ir.IntType(32)
        self.int8_type = ir.IntType(8)
        self.int16_type = ir.IntType(16)
        self.int32_type = ir.IntType(32)
        self.int64_type = ir.IntType(64)
        self.float_type = ir.FloatType()
        self.double_type = ir.DoubleType()
        self.bool_type = ir.IntType(1)
        
        self.string_counter = 0
        self.symbol_table = {}
        self.global_strings = []

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
        
    def get_var_ptr(self, var_name):
        """Gets the pointer to a variable in the symbol table."""
        if var_name in self.variables:
            return self.variables[var_name][0]
        return None
        
    def get_llvm_type(self, data_type):
        """Gets the LLVM type for a data type string."""
        return str(self.type_map.get(data_type, ir.IntType(32)))
        
    def get_next_temp(self):
        """Gets the next temporary variable name."""
        name = f"%tmp{self.temp_counter}"
        self.temp_counter += 1
        return name

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
        elif isinstance(stmt, MatchStatement):
            self.generate_match_statement(stmt)
        elif isinstance(stmt, ClassDeclaration):
            self.generate_class_declaration(stmt)
        elif isinstance(stmt, DataclassDeclaration):
            self.generate_dataclass_declaration(stmt)
        elif isinstance(stmt, ImportStatement):
            self.generate_import_statement(stmt)
        else:
            print(f"Warning: Unsupported statement type: {type(stmt)}")
            
    def generate_match_statement(self, stmt: MatchStatement) -> None:
        """Generates code for match statements (similar to switch)"""
        # Get the match value
        match_value = self.generate_expression(stmt.value)
        
        # Create a merge block for after all cases
        merge_block = self.builder.append_basic_block(f"match_end.{self.temp_counter}")
        self.temp_counter += 1
        
        # Create default block if there's an else clause
        default_block = None
        
        # First collect all case blocks
        case_blocks = []
        default_block = None
        
        for case in stmt.cases:
            if hasattr(case, 'value') and case.value != 'ELSE':
                block = self.builder.append_basic_block(f"match_case.{self.temp_counter}")
                self.temp_counter += 1
                case_blocks.append((case.value, block))
            else:
                # Default/else case
                default_block = self.builder.append_basic_block(f"match_default.{self.temp_counter}")
                self.temp_counter += 1
        
        # If no default, create an empty one
        if not default_block:
            default_block = self.builder.append_basic_block(f"match_default.{self.temp_counter}")
            self.temp_counter += 1
            
        # Start with a cascade of if-else comparisons
        current_block = self.builder.block
        
        # For each case, add comparison and branch
        for case_value, case_block in case_blocks:
            case_const = self.generate_expression(case_value)
            
            # Compare the match value with this case value
            cmp_result = self.builder.icmp_signed('==', match_value, case_const)
            
            # Create a new block for the next comparison if there are more cases
            next_check = self.builder.append_basic_block(f"match_next.{self.temp_counter}")
            self.temp_counter += 1
            
            # Branch based on the comparison
            self.builder.cbranch(cmp_result, case_block, next_check)
            
            # Position at next check block
            self.builder.position_at_end(next_check)
        
        # Add branch to default block at the end of the cascade
        self.builder.branch(default_block)
        
        # Now generate code for each case body
        for i, (case_value, case_block) in enumerate(case_blocks):
            self.builder.position_at_end(case_block)
            # Find the corresponding case in the AST
            for case in stmt.cases:
                if hasattr(case, 'value') and case.value == case_value:
                    # Generate the case body
                    if hasattr(case, 'body'):
                        for body_stmt in case.body:
                            self.generate_statement(body_stmt)
                    break
            # Branch to merge block
            self.builder.branch(merge_block)
            
        # Generate default case
        self.builder.position_at_end(default_block)
        # Find the default case in the AST
        for case in stmt.cases:
            if not hasattr(case, 'value') or case.value == 'ELSE':
                # Generate default case body
                if hasattr(case, 'body'):
                    for body_stmt in case.body:
                        self.generate_statement(body_stmt)
                break
        
        # Branch to merge block
        self.builder.branch(merge_block)
        
        # Continue at the merge point
        self.builder.position_at_end(merge_block)
            
    def generate_class_declaration(self, stmt: ClassDeclaration) -> None:
        """Generates code for class declarations"""
        # For now, we'll track classes in a simple way
        # We store the structure type for future use
        field_types = []
        
        # Create a new structure type for this class
        struct_type = ir.LiteralStructType(field_types)
        
        # Store the class definition for future use
        self.types[stmt.name] = struct_type
        
        # In a real system, we'd generate methods too
        # But for our simple compiler, we just store the structure
        print(f"Defined class {stmt.name}")
        
    def generate_dataclass_declaration(self, stmt: DataclassDeclaration) -> None:
        """Generates code for dataclass declarations (similar to struct)"""
        # Simple generation similar to class
        field_types = []
        
        # Create a new structure type for this dataclass
        struct_type = ir.LiteralStructType(field_types)
        
        # Store the class definition for future use
        if not hasattr(self, 'types'):
            self.types = {}
        self.types[stmt.name] = struct_type
        
        print(f"Defined dataclass {stmt.name}")
        
    def generate_import_statement(self, stmt: ImportStatement) -> None:
        """Generates code for import statements"""
        # In a real system, we'd handle linking to other modules
        # For now, we'll just print what's being imported
        if hasattr(stmt, 'elements') and stmt.elements:
            elements = ', '.join(elem for elem in stmt.elements) if isinstance(stmt.elements, list) else stmt.elements
            module = stmt.module if hasattr(stmt, 'module') else ""
            print(f"Importing {elements} from {module}")
        else:
            module = stmt.module if hasattr(stmt, 'module') else ""
            print(f"Importing {module}")

    def generate_comment(self, stmt: str) -> None:
        """ Adds a comment """
        pass  # LLVM IR doesn't support comments directly

    def generate_var_declaration(self, stmt: VarDeclaration) -> None:
        """ Creates a variable and stores it in the 'variables' map """
        data_type = stmt.data_type or self.infer_type(stmt.value)
        
        # Handle the variable allocation based on its type
        if data_type == "STRING":
            # For strings, we allocate a pointer to string (char*)
            ptr = self.builder.alloca(ir.IntType(8).as_pointer(), name=stmt.name)
            self.variables[stmt.name] = (ptr, data_type)
            
            if stmt.value:
                value = self.generate_expression(stmt.value)
                self.builder.store(value, ptr)
        else:
            # For other types (INT, FLOAT, BOOL, etc.)
            llvm_type = self.type_map.get(data_type, ir.IntType(32))
            ptr = self.builder.alloca(llvm_type, name=stmt.name)
            self.variables[stmt.name] = (ptr, data_type)
            
            if stmt.value:
                value = self.generate_expression(stmt.value)
                # Convert if types don't match
                value = self.convert_type(value, data_type)
                self.builder.store(value, ptr)

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
        self.builder.position_at_end(if_then)
        for then_stmt in stmt.then_body:
            self.generate_statement(then_stmt)
        self.builder.branch(merge_block)

        # Generate the else block if it exists
        if if_else:
            self.builder.position_at_end(if_else)
            for else_stmt in stmt.else_body:
                self.generate_statement(else_stmt)
            self.builder.branch(merge_block)

        # Continue at the merge point
        self.builder.position_at_end(merge_block)

    def generate_while_statement(self, stmt: WhileStatement) -> None:
        """Generates LLVM IR for a while loop"""
        # Create basic blocks for the loop
        while_cond = self.builder.append_basic_block("while_cond")
        while_body = self.builder.append_basic_block("while_body")
        while_end = self.builder.append_basic_block("while_end")
        
        # Branch to condition block
        self.builder.branch(while_cond)
        
        # Emit condition code
        self.builder.position_at_end(while_cond)
        cond_val = self.generate_expression(stmt.condition)
        
        # Convert to boolean if needed
        if cond_val.type != ir.IntType(1):
            if cond_val.type == ir.FloatType():
                cond_bool = self.builder.fcmp_ordered('!=', cond_val, ir.Constant(ir.FloatType(), 0.0))
            else:
                cond_bool = self.builder.icmp_signed('!=', cond_val, ir.Constant(cond_val.type, 0))
        else:
            cond_bool = cond_val
            
        # Branch to body or end based on condition
        self.builder.cbranch(cond_bool, while_body, while_end)
        
        # Emit the loop body
        self.builder.position_at_end(while_body)
        for body_stmt in stmt.body:
            self.generate_statement(body_stmt)
            
        # Jump back to condition
        self.builder.branch(while_cond)
        
        # Continue from end block
        self.builder.position_at_end(while_end)

    def generate_for_statement(self, stmt: ForStatement) -> None:
        """Generates LLVM IR for a for loop"""
        # Extract the loop variable name
        loop_var_name = None
        for attr in stmt.attributes:
            if attr.name == "name":
                loop_var_name = attr.value
                break
                
        if not loop_var_name:
            raise Exception("For loop missing variable name")
            
        # Create basic blocks for the loop
        for_setup = self.builder.append_basic_block("for_setup")
        for_cond = self.builder.append_basic_block("for_cond")
        for_body = self.builder.append_basic_block("for_body")
        for_update = self.builder.append_basic_block("for_update")
        for_end = self.builder.append_basic_block("for_end")
        
        # If the loop value is a Range, we'll handle it specially
        is_range = isinstance(stmt.value, Range)
        
        if is_range:
            # Branch to setup block first
            self.builder.branch(for_setup)
            
            # Position at setup block
            self.builder.position_at_end(for_setup)
            
            # Allocate the loop counter
            counter_ptr = self.builder.alloca(ir.IntType(32), name=loop_var_name)
            
            # Generate code for range start and end
            start_val = self.generate_expression(stmt.value.start)
            end_val = self.generate_expression(stmt.value.end)
            
            # Get step value (default to 1)
            if stmt.value.step:
                step_val = self.generate_expression(stmt.value.step)
            else:
                step_val = ir.Constant(ir.IntType(32), 1)
                
            # Store the initial value
            self.builder.store(start_val, counter_ptr)
            
            # Remember the variable for use in the loop body
            self.variables[loop_var_name] = (counter_ptr, "INT")
            
            # Jump to the condition check
            self.builder.branch(for_cond)
            
            # Condition check: i < end
            self.builder.position_at_end(for_cond)
            current_val = self.builder.load(counter_ptr)
            cond = self.builder.icmp_signed('<', current_val, end_val)
            self.builder.cbranch(cond, for_body, for_end)
            
            # Loop body
            self.builder.position_at_end(for_body)
            # Generate the loop body statements
            for body_stmt in stmt.body:
                self.generate_statement(body_stmt)
            self.builder.branch(for_update)
            
            # Update the counter: i += step
            self.builder.position_at_end(for_update)
            current_val = self.builder.load(counter_ptr)
            next_val = self.builder.add(current_val, step_val)
            self.builder.store(next_val, counter_ptr)
            self.builder.branch(for_cond)
            
            # After the loop
            self.builder.position_at_end(for_end)
            
            # Remove the loop variable from scope
            if loop_var_name in self.variables:
                del self.variables[loop_var_name]
        else:
            # Handle other types of for loops (iterating over collections, etc.)
            print("Warning: For loops over non-range values not implemented yet")
            # Make sure we branch somewhere to avoid invalid IR
            self.builder.branch(for_end)
            self.builder.position_at_end(for_end)

    def generate_expression(self, expr):
        """Generate code for an expression."""
        if isinstance(expr, Token):
            if expr.type == "INT":
                return ir.Constant(ir.IntType(32), int(expr.value))
            elif expr.type == "FLOAT":
                return ir.Constant(ir.FloatType(), float(expr.value))
            elif expr.type == "STRING":
                # Create a global string constant
                string_val = expr.value
                string_bytes = bytearray((string_val + '\0').encode('utf8'))
                str_type = ir.ArrayType(ir.IntType(8), len(string_bytes))
                
                # Add the string as a global constant
                global_fmt = ir.GlobalVariable(self.module, str_type, name=f".str.{self.string_counter}")
                global_fmt.global_constant = True
                global_fmt.linkage = 'private'
                global_fmt.initializer = ir.Constant(str_type, string_bytes)
                self.string_counter += 1
                
                # Get a pointer to the first character
                zero = ir.Constant(ir.IntType(32), 0)
                return self.builder.gep(global_fmt, [zero, zero])
            elif expr.type == "BOOL":
                # Handle boolean values properly
                if isinstance(expr.value, str):
                    bool_val = expr.value.lower() == "true"
                else:
                    bool_val = bool(expr.value)
                return ir.Constant(ir.IntType(1), 1 if bool_val else 0)
            elif expr.type == "IDENTIFIER":
                # Load the value from the variable
                var_name = expr.value
                if var_name in self.variables:
                    ptr, _ = self.variables[var_name]
                    return self.builder.load(ptr)
                elif var_name == "null":
                    # Special case for null value
                    return ir.Constant(ir.IntType(32), 0)
                else:
                    print(f"Warning: Variable '{var_name}' not found in symbol table")
                    return ir.Constant(ir.IntType(32), 0)  # Default for unknown variables
        elif isinstance(expr, BinaryOperation):
            # Generate code for the operands
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            
            # If types don't match, convert them
            left_type = left.type
            right_type = right.type
            
            # Handle operations based on the operator and operand types
            if expr.operator == "PLUS":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fadd(left, right)
                else:
                    return self.builder.add(left, right)
            elif expr.operator == "MINUS":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fsub(left, right)
                else:
                    return self.builder.sub(left, right)
            elif expr.operator == "MUL":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fmul(left, right)
                else:
                    return self.builder.mul(left, right)
            elif expr.operator == "DIV":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fdiv(left, right)
                else:
                    return self.builder.sdiv(left, right)
            # Comparison operators
            elif expr.operator == "EQUAL":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fcmp_ordered('==', left, right)
                else:
                    return self.builder.icmp_signed('==', left, right)
            elif expr.operator == "NOT_EQUAL":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fcmp_ordered('!=', left, right)
                else:
                    return self.builder.icmp_signed('!=', left, right)
            elif expr.operator == "LESS_THAN":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fcmp_ordered('<', left, right)
                else:
                    return self.builder.icmp_signed('<', left, right)
            elif expr.operator == "LESS_THAN_EQUAL":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fcmp_ordered('<=', left, right)
                else:
                    return self.builder.icmp_signed('<=', left, right)
            elif expr.operator == "GREATER_THAN":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fcmp_ordered('>', left, right)
                else:
                    return self.builder.icmp_signed('>', left, right)
            elif expr.operator == "GREATER_THAN_EQUAL":
                if left_type == ir.FloatType() or right_type == ir.FloatType():
                    # Convert to float if needed
                    if left_type != ir.FloatType():
                        left = self.builder.sitofp(left, ir.FloatType())
                    if right_type != ir.FloatType():
                        right = self.builder.sitofp(right, ir.FloatType())
                    return self.builder.fcmp_ordered('>=', left, right)
                else:
                    return self.builder.icmp_signed('>=', left, right)
            elif expr.operator == "NULL_COALESCING":
                # Implement null coalescing operator: left ?? right
                # If left is null, return right, otherwise return left
                
                # Create blocks for the null check
                null_check = self.builder.append_basic_block(f"null_check.{self.temp_counter}")
                not_null = self.builder.append_basic_block(f"not_null.{self.temp_counter}")
                end_block = self.builder.append_basic_block(f"end_null_coalescing.{self.temp_counter}")
                self.temp_counter += 1
                
                # Allocate space for result
                result_type = right_type if right_type != ir.IntType(1) else ir.IntType(32)
                result_ptr = self.builder.alloca(result_type)
                
                # Check if left is null (equals 0)
                null_value = ir.Constant(left.type, 0)
                is_null = self.builder.icmp_signed('==', left, null_value)
                self.builder.cbranch(is_null, null_check, not_null)
                
                # If null, use right value
                self.builder.position_at_end(null_check)
                if right_type != result_type:
                    right_converted = self.builder.zext(right, result_type) if right_type == ir.IntType(1) else right
                else:
                    right_converted = right
                self.builder.store(right_converted, result_ptr)
                self.builder.branch(end_block)
                
                # If not null, use left value
                self.builder.position_at_end(not_null)
                if left_type != result_type:
                    left_converted = self.builder.zext(left, result_type) if left_type == ir.IntType(1) else left
                else:
                    left_converted = left
                self.builder.store(left_converted, result_ptr)
                self.builder.branch(end_block)
                
                # Continue from the end block
                self.builder.position_at_end(end_block)
                return self.builder.load(result_ptr)
            else:
                print(f"Warning: Unsupported binary operator: {expr.operator}")
                return ir.Constant(ir.IntType(32), 0)
                
        elif isinstance(expr, FunctionCall):
            if expr.name == "print":
                # Handle print function
                if expr.arguments:
                    # Get the printf function from the module
                    printf_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
                    printf = self.module.get_global("printf") 
                    if not printf:
                        printf = ir.Function(self.module, printf_ty, name="printf")
                    
                    # Process argument
                    arg = self.generate_expression(expr.arguments[0])
                    
                    # Create format string based on argument type
                    if isinstance(arg.type, ir.FloatType):
                        fmt_str = "%f\\00"
                    elif isinstance(arg.type, ir.IntType):
                        fmt_str = "%d\\00"
                    else:
                        fmt_str = "%s\\00"
                    
                    # Create global format string
                    fmt_constant = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_str)), bytearray(fmt_str.encode("utf8")))
                    fmt_var = ir.GlobalVariable(self.module, fmt_constant.type, name=f".str.{self.string_counter}")
                    fmt_var.linkage = "private"
                    fmt_var.global_constant = True
                    fmt_var.initializer = fmt_constant
                    self.string_counter += 1
                    
                    # Get pointer to the format string
                    zero = ir.Constant(ir.IntType(32), 0)
                    fmt_ptr = self.builder.gep(fmt_var, [zero, zero])
                    
                    # Call printf
                    self.builder.call(printf, [fmt_ptr, arg])
                    
                return ir.Constant(ir.IntType(32), 0)
                
            # Default for unknown functions
            print(f"Warning: Unknown function: {expr.name}")
            return ir.Constant(ir.IntType(32), 0)
            
        else:
            # Unhandled expression type
            print(f"Warning: Unsupported expression type: {type(expr)}")
            return ir.Constant(ir.IntType(32), 0)

    def generate_unary_operation(self, stmt: UnaryOperation) -> None:
        """Generates code for unary operations like increment/decrement"""
        var_name = stmt.identifier
        if var_name not in self.variables:
            raise Exception(f"Variable {var_name} not declared!")
            
        ptr, var_type = self.variables[var_name]
        llvm_type = self.type_map.get(var_type, ir.IntType(32))
        
        # Load the current value
        current_val = self.builder.load(ptr)
        
        # Apply the operation
        if stmt.operator == "INCREMENT":
            one = ir.Constant(llvm_type, 1)
            new_val = self.builder.add(current_val, one)
        elif stmt.operator == "DECREMENT":
            one = ir.Constant(llvm_type, 1)
            new_val = self.builder.sub(current_val, one)
        else:
            raise Exception(f"Unsupported unary operation: {stmt.operator}")
            
        # Store the result back
        self.builder.store(new_val, ptr)
        
    def generate_function_call(self, stmt: FunctionCall) -> None:
        """Generates code for function calls"""
        if stmt.name == "print":
            # Special handling for print function
            if not stmt.arguments:
                # Print newline if no arguments
                printf = self.module.get_global("printf")
                fmt_str = "\\n\\00"
                fmt_constant = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_str)), 
                                          bytearray(fmt_str.encode("utf8")))
                fmt_var = ir.GlobalVariable(self.module, fmt_constant.type, 
                                          name=f".str.{self.string_counter}")
                fmt_var.linkage = "private"
                fmt_var.global_constant = True
                fmt_var.initializer = fmt_constant
                self.string_counter += 1
                
                # Get pointer to the format string
                zero = ir.Constant(ir.IntType(32), 0)
                fmt_ptr = self.builder.gep(fmt_var, [zero, zero])
                
                # Call printf with just the format string
                self.builder.call(printf, [fmt_ptr])
            else:
                # This is already handled in generate_expression for now
                self.generate_expression(stmt)
        else:
            # For other functions, generate the expression which will handle the call
            self.generate_expression(stmt)

    def generate_import_statement(self, stmt):
        """Generate code for import statements"""
        # In a real compiler, this would load external modules
        # For now, we'll just create a placeholder that acknowledges the import
        
        target = stmt.target if hasattr(stmt, 'target') else "unknown"
        language = stmt.language if hasattr(stmt, 'language') else None
        
        # Log the import for debugging purposes
        if language:
            print(f"Import '{target}' from language '{language}' processed")
        else:
            print(f"Import '{target}' processed")
        
        return None