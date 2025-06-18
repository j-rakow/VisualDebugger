import subprocess
import os
import re

'''
FUNCTION: find_executable()
INPUT: N/A
OUTPUT: Name of the most recently modified .out file (string), or None if none are found

This function searches the current working directory for files ending with '.out',
which are typically compiled executables. Among those, it identifies and returns
the most recently modified one based on its last modified timestamp. If no such
files are found, it prints an error message and returns None.
'''

def find_executable():
    # Lists all files and directories in the current working directory.
    files = os.listdir()

    # Filters the list to only include files (not directories) that end with .out 
    # (commonly used extension for compiled executables in Unix-based systems).
    executables = [f for f in files if f.endswith('.out') and os.path.isfile(f)]
    # Checks if no .out files were found. If none, it prints an error message and returns None.
    if not executables:
        print("No executable file found.")
        return None
    
    # Finds the most recently modified .out file by comparing their last modification timestamps.
    most_recent = max(executables, key=lambda f: os.path.getmtime(f))
    return most_recent



'''
FUNCTION: run_valgrind()
INPUT: N/A
OUTPUT: None (prints Valgrind memory analysis results to console)

This function runs Valgrind on the most recently modified '.out' file in the current directory.

Steps:
1. Calls find_executable() to locate the latest compiled program.
2. If found, executes Valgrind with full leak checking and origin tracking.
3. Captures the Valgrind output and extracts the number of memory errors and their contexts
   using get_num_errors_and_contexts().
4. Prints a success message if no errors are found; otherwise, prints an error summary.
'''

def run_valgrind():
    # Get the most recently modified '.out' executable in the current directory
    executable = find_executable()

    # If an executable is found, proceed with memory checking
    if executable:
        print(f"Running Valgrind on {executable}...\n")

        # Run Valgrind with options to perform a full memory leak check
        # and track origins of uninitialized values
        result = subprocess.run(
            ['valgrind', '--leak-check=full', '--track-origins=yes', f'./{executable}'],
            stdout=subprocess.PIPE,               # Capture standard output
            stderr=subprocess.PIPE,               # Capture standard error (Valgrind's main output)
            text=True                             # Return output as strings instead of bytes
        )
       
        # Valgrind writes diagnostic info to stderr, so capture that output
        output = result.stderr
        
        # Analyze the Valgrind output to count memory errors and their contexts
        num_errors, num_contexts = get_num_errors_and_contexts(output)

        # Report results to the user
        if num_errors == 0:
            print("✅ Valgrind: No errors detected!")
        else:
            print(f"❌ Valgrind: {num_errors} errors in {num_contexts} contexts.\n")
    else:
        # If no executable was found, notify the user
        print("No executable found to run.")


'''
FUNCTION: get_num_errors_and_contexts(output)

INPUT: 
    the stderr string produced by running Valgrind

OUTPUT:
    (int, int) a tuple containing:
        - the number of memory errors detected by Valgrind
        - the number of contexts (unique error points) in which those errors occurred

DESCRIPTION:
This function parses Valgrind output to extract the memory error summary. It looks
for a line in the form:
    "ERROR SUMMARY: X errors from Y contexts"
using regular expressions.

If such a line is found, it extracts the two integers X and Y and returns them
as a tuple. If no summary line is found, it assumes no errors and returns (0, 0).
This is used to summarize the results of a Valgrind memory check in a programmatic way.
'''

def get_num_errors_and_contexts(output):
    # Regex to match the Valgrind error summary line, e.g.,
    # "ERROR SUMMARY: 3 errors from 2 contexts"
    error_summary_regex = re.compile(r"ERROR SUMMARY: [0-9]+ errors from [0-9]+ contexts")

    # Regex to extract numbers from a string
    number_regex = re.compile(r"[0-9]+")

    # Search the output for the error summary line
    error_string = error_summary_regex.findall(output)

    # If the summary is not found, assume 0 errors and 0 contexts
    if not error_string:
        return 0, 0

    # Extract the numbers from the matched summary line
    error_nums = number_regex.findall(error_string[0])

    # Convert the extracted strings to integers
    num_errors = int(error_nums[0])
    num_contexts = int(error_nums[1])

    # Return a tuple: (number of errors, number of contexts)
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
    line_regex = re.compile(r"__libc_start_call_main")

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
    roadMap = []
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

        lineArrLen = len(first_line_arr)
        for i,line in enumerate(first_line_arr):
            if i == lineArrLen -1:
                roadMap.append("next")
            else:
                roadMap.append("step")
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

                lineArrLen = len(first_line_arr)
                for i,line in enumerate(first_line_arr):
                    if i == lineArrLen -1:
                        roadMap.append("next")
                    else:
                        roadMap.append("step")
                    print(f"Line: {line}")
                for line in line_arr:
                    print(f"Line: {line}")
            except subprocess.TimeoutExpired:
                print("❌ GDB timed out while waiting for the second breakpoint.")
                return roadMap
        return roadMap
        
    else:
        print("No executable to debug.")

run_valgrind()
roadMap = run_gdb_analysis()
print(f"Here is the roadMap: {roadMap}")
