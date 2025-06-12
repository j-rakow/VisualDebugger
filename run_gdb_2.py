import gdb


def is_user_function(frame):
        filename = frame
        print("📂 File:", filename)
        if not filename.startswith("/usr/") and "glibc" not in filename and "libc" not in filename:
            print("✅ This is a user-defined function.")
        else:
            print("❌ This is a library/system function.")




def run_gdb_2():
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
            print(f"📍 {filename}:{line} — in function '{func}'")

            # Optional: print if it's a user-defined function
            if is_user_function(func):
                print(f"✅ User-defined function: {filename}")
            elif func == "main":
                print(f"✅ User-defined function: {filename}")
            else:
                print(f"⛔ Library/system function: {func}")
                break

            if index == 0:
                gdb.execute("next")
            else:
                gdb.execute("step")
            index+=1
    except gdb.error as e:
        print(f"⚠️  GDB Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")