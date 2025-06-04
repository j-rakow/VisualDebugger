import subprocess
import os
import re


def find_executable():
    # Get a list of all files in the current directory
    files = os.listdir()
   
    # Filter out files that have an executable extension (e.g., .out, .exe, or no extension)
    executables = [f for f in files if os.path.isfile(f) and (f.endswith('.out') or f.endswith('.exe') or os.access(f, os.X_OK))]
   
    if not executables:
        print("No executable file found.")
        return None
   
    # If multiple executables, return the most recently modified one
    most_recent = max(executables, key=lambda f: os.path.getmtime(f))
    return most_recent


def run_valgrind():
    executable = find_executable()
    if executable:
        print(f"Running Valgrind on {executable}...")
        result = subprocess.run(['valgrind', '--leak-check=full', '--track-origins=yes', f'./{executable}'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Valgrind Output:")
        print(result.stdout)
        output = result.stderr
        parse_valgrind(output)
    else:
        print("No executable found to run.")


def parse_valgrind(output):
   
    num_errors,num_contexts = get_num_errors_and_contexts(output)


    if num_errors == 0:
        print("Congratulations, there are no errors!")
    else:
         print("There are ", num_errors, " errors in ", num_contexts, " contexts")


    print(output)


   
def get_num_errors_and_contexts(output):


    #regex representing: ERROR SUMMARY: 0 errors from 0 contexts
    error_summary_regex = re.compile(r"ERROR SUMMARY: [0-9]* errors from [0-9]* contexts")
    #regex representing numbers
    number_regex = re.compile(r"[0-9]+")


    #extracting numbers from string
    error_string = error_summary_regex.findall(output)


    #list of numbers in the string
    error_nums = number_regex.findall(error_string[0])


    num_errors = int(error_nums[0])
    num_contexts = int(error_nums[1])


    return (num_errors,num_contexts)


run_valgrind()