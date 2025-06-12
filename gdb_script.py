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

def is_EOF(output):
    line_regex = re.compile(r"Reached end of valid source.")

    line_string = line_regex.findall(output)

    if not line_string:
        return False
    else:
        return True

def is_Error(output):
    line_regex_1 = re.compile(r"💥 Unexpected error: {e}")
    line_regex_2 = re.compile(r"⚠️  GDB Error: {e}")


    line_string_1 = line_regex_1.findall(output)
    line_string_2 = line_regex_2.findall(output)

    if not line_string_1 and not line_string_2:
        return False
    else:
        return True

    
def run_gdb_analysis():
    executable = find_executable()
    if executable:
        with open("gdb_script.txt", "w") as f:
            f.write(
                "set pagination off\n"
                "break main\n"
                "run\n"
                "source run_gdb_1.py\n"
                "python run_gdb_1()\n"
                "quit\n"
            )

        print(f"\nRunning GDB on {executable}...\n")
        result = subprocess.run(
            ["gdb", "-q", "-batch", "-x", "gdb_script.txt", f"./{executable}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output= result.stdout
        first_line_arr = get_line_numbers(output)

        for line in first_line_arr:
            print(f"Line: {line}")
        #add code here to handle errors


        next_line = 0
        line_arr = first_line_arr

        output2 = ""

        while not is_EOF(output2) and not is_Error(output2):
            if len(line_arr) == 1:
                next_line = line_arr[0]
            else:
                next_line = line_arr[-2]

            print(f"Next line: {next_line}")
            
            breakpoint_str = f"break {next_line}\n"

            with open("gdb_script.txt", "w") as f:
                f.write(
                    "set pagination off\n"
                    + breakpoint_str +
                    "run\n"
                    "source run_gdb_2.py\n"
                    "python run_gdb_2()\n"
                    "quit\n"
                )
            try:
                result2 = subprocess.run(
                    ["gdb", "-q", "-batch", "-x", "gdb_script.txt", f"./{executable}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    timeout=10
                )
                output2 = result2.stdout

                line_arr = get_line_numbers(output2)
                # print(output2)

                for line in line_arr:
                    print(f"Line: {line}")
            except subprocess.TimeoutExpired:
                print("❌ GDB timed out while waiting for the second breakpoint.")
                return  
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
