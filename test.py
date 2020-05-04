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

    f = open(output_file, "r")
    output_text = f.read()
    f.close()

    prog_output = subprocess.check_output(['python', 'main.py', input_file]).decode("ascii").replace("\r\n","\n")

    return prog_output == output_text

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
