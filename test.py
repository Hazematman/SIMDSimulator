#!/usr/bin/env python3
import sys
import os
import subprocess
import difflib

test_dir = "./tests/"
d = difflib.Differ()

def run_test(test):
    test_path = "{}{}".format(test_dir, test)
    input_file = "{}/{}".format(test_path, "input.txt")
    output_file = "{}/{}".format(test_path, "output.txt")
    memory_file = "{}/{}".format(test_path, "memory.txt")
    
    cmd = ['python', 'main.py', input_file]
    if os.path.isfile(memory_file):
        cmd.append(memory_file)

    f = open(output_file, "r")
    output_text = f.read()
    f.close()

    prog_output = subprocess.check_output(cmd).decode("ascii").replace("\r\n","\n")
    
    result = (prog_output == output_text)
    
    if not result:
        print("GOT")
        print(prog_output)
        print("Expected")
        print(output_text)

    return result

def main():
    tests = os.listdir("./tests/")
    
    for test in tests:
        if(run_test(test)):
            print("Test '{}' passed".format(test))
        else:
            print("Test '{}' failed".format(test))

    return 0

if __name__ == "__main__":
    sys.exit(main())
