from llvmlite import ir, binding


# SETUP
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

module = ir.Module(name="pym_module")
module.triple = binding.get_default_triple()

# Define function: int main()
func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
function = ir.Function(module, func_type, name="main")
block = function.append_basic_block(name="entry")
builder = ir.IRBuilder(block)




# Actual inserted LLVM code: return 42
if_true = function.append_basic_block(name="if_true")
if_false = function.append_basic_block(name="if_false")
merge_block = function.append_basic_block(name="merge")
x = function.args[0]
# Compare: if (x > 10)
cond = builder.icmp_signed('>', x, ir.Constant(ir.IntType(32), 10))
# Conditional branch
builder.cbranch(cond, if_true, if_false)
# if_true block: result = 42
builder.position_at_end(if_true)
true_val = ir.Constant(ir.IntType(32), 42)
builder.branch(merge_block)  # Jump to merge_block
# if_false block: result = 0
builder.position_at_end(if_false)
false_val = ir.Constant(ir.IntType(32), 0)
builder.branch(merge_block)  # Jump to merge_block
# Merge block
builder.position_at_end(merge_block)
phi = builder.phi(ir.IntType(32))  # Phi node to select result
phi.add_incoming(true_val, if_true)
phi.add_incoming(false_val, if_false)
builder.ret(phi)



print(module)
print("-----------------------------")
llvm_ir = str(module)
llvm_mod = binding.parse_assembly(llvm_ir)  # Convert to ModuleRef
llvm_mod.verify()
target = binding.Target.from_default_triple()
machine = target.create_target_machine()
assembly = machine.emit_assembly(llvm_mod)
print("Assembly:\n", assembly)