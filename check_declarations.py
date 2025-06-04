# check_declarations.py
import gdb

def check_declarations(block, line):
    print(f"\n🔍 GDB: Current line = {line}")
    while block:
        for sym in block:
            if sym.is_variable:
                try:
                    declared_line = sym.line
                    status = "✅ declared" if declared_line <= line else "⏳ not declared yet"
                    print(f"    • {sym.print_name} — line {declared_line} — {status}")
                except Exception as e:
                    print(f"    • {sym.print_name} — line unknown ({e})")
        block = block.superblock
