# check_declarations.py
import gdb

# def run_gdb(block, line):
#     print(f"\n🔍 GDB: Current line = {line}")
#     while block:
#         for sym in block:
#             if sym.is_variable:
#                 try:
#                     declared_line = sym.line
#                     status = "✅ declared" if declared_line <= line else "⏳ not declared yet"
#                     print(f"    • {sym.print_name} — line {declared_line} — {status}")
#                 except Exception as e:
#                     print(f"    • {sym.print_name} — line unknown ({e})")
#         block = block.superblock

def is_user_function(frame):
        filename = frame
        print("📂 File:", filename)
        if not filename.startswith("/usr/") and "glibc" not in filename and "libc" not in filename:
            print("✅ This is a user-defined function.")
        else:
            print("❌ This is a library/system function.")


def run_gdb_1():
    index = 0
    try:
        while True:
            frame = gdb.selected_frame()
            sal = frame.find_sal()

            # Exit if we reached an invalid location or end of user code
            if not sal.is_valid() or sal.line == 0 or sal.symtab is None:
                print("🛑 Reached end of valid source.")
                break

            func = frame.name()
            filename = sal.symtab.filename
            line = sal.line
            print(f"This is the gdb line output: {line} at {index}")
            index+=1
            print(f"📍 {filename}:{line} — in function '{func}'")

            # Optional: print if it's a user-defined function
            if is_user_function(func):
                print(f"✅ User-defined function: {filename}")
            elif func == "main":
                print(f"✅ User-defined function: {filename}")
            else:
                print(f"⛔ Library/system function: {func}")
                break

            gdb.execute("step")
    except gdb.error as e:
        print(f"⚠️  GDB Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
