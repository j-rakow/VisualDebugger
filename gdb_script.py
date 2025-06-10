import subprocess
import os
import re


def find_executable():
    files = os.listdir()
    executables = [f for f in files if f.endswith('.out') and os.path.isfile(f)]
    if not executables:
        print("No executable file found.")
        return None
    most_recent = max(executables, key=lambda f: os.path.getmtime(f))
    return most_recent


def run_valgrind():
    executable = find_executable()
    if executable:
        print(f"Running Valgrind on {executable}...\n")
        result = subprocess.run(
            ['valgrind', '--leak-check=full', '--track-origins=yes', f'./{executable}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = result.stderr
        num_errors, num_contexts = get_num_errors_and_contexts(output)
        if num_errors == 0:
            print("✅ Valgrind: No errors detected!")
        else:
            print(f"❌ Valgrind: {num_errors} errors in {num_contexts} contexts.\n")
    else:
        print("No executable found to run.")


def get_num_errors_and_contexts(output):
    error_summary_regex = re.compile(r"ERROR SUMMARY: [0-9]+ errors from [0-9]+ contexts")
    number_regex = re.compile(r"[0-9]+")
    error_string = error_summary_regex.findall(output)
    if not error_string:
        return 0, 0
    error_nums = number_regex.findall(error_string[0])
    num_errors = int(error_nums[0])
    num_contexts = int(error_nums[1])
    return (num_errors, num_contexts)

#returns an array with the line numbers of the gdb step/next
def get_line_numbers(output):
    line_regex = re.compile(r"This is the gdb line output: [0-9]+ at [0-9+]")
    number_regex = re.compile(r"[0-9]+")
    line_arr = []

    line_string = line_regex.findall(output)
    
    for line in line_string:
        line_nums = number_regex.findall(line)
        line_num = line_nums[0]
        line_arr.append(line_num)
    return line_arr

    
def run_gdb_analysis():
    executable = find_executable()
    if executable:
        with open("gdb_script.txt", "w") as f:
            f.write(
                "set pagination off\n"
                "break main\n"
                "run\n"
                "source run_gdb.py\n"
                "python run_gdb()\n"
                "quit\n"
            )

        print(f"\nRunning GDB on {executable}...\n")
        result = subprocess.run(
            ["gdb", "-q", "-x", "gdb_script.txt", f"./{executable}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # print(result.stdout)
        line_arr = get_line_numbers(result.stdout)

        for line in line_arr:
            print(f"Line: {line}")
    else:
        print("No executable to debug.")


# def run_gdb_analysis():
#     executable = find_executable()
#     if executable:
#         with open("gdb_script.txt", "w") as f:
                
                
#                 f.write("""
#                 set pagination off
#                 break main
#                 run
#                 source run_gdb.py
#                 python run_gdb(gdb.selected_frame().block(), gdb.selected_frame().find_sal().line)
#                 """)
#                 f.write("""quit""")

#         print(f"\nRunning GDB on {executable}...\n")
#         result = subprocess.run(
#             ["gdb", "-q", "-x", "gdb_script.txt", f"./{executable}"],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#         )
#         print(result.stdout)
#     else:
#         print("No executable to debug.")

# Run both analyses
run_valgrind()
run_gdb_analysis()
