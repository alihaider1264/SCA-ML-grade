import argparse
import pandas as pd
import numpy as np
import os
import tensorflow as tf
import keras
from keras.preprocessing.text import tokenizer_from_json


parser = argparse.ArgumentParser(description='Token Category Generator')

parser.add_argument('-i', '--input', type=str, required=True,
                    help='Input file path')
parser.add_argument('-o', '--output', type=str, required=False,
                    help='Output file path')

tokenGroups = []

def initTokenGroups():

    #Group for numbers 1 through 100 as strings
    numbArray = []
    for i in range(1, 101):
        numbArray.append([str(i)])
    tokenGroups.append(numbArray)
    #Group for Literals
    tokenGroups.append(["\"strlit\"", "\'numlit\'", 
    ])
    #Group for grouping
    tokenGroups.append([ "var1", "funct1", 'class1'])
    #Group for operators
    tokenGroups.append([ "+", "-", "*", "/", "%", "**", "//", "@", "<<", ">>", "&", "|", "^", "~", "<", ">", 
                    "<=", ">=", "==", "!=", ",", ":", ".", ";", "=", "+=", "-=", 
                    "*=", "/=", "%=", "**=", "//=", "@=", "&=", "|=", "^=", ">>=", "<<=",
    ])
    #Group for flow control statements
    tokenGroups.append(["if", "else", "elif", "while", "for", "in", "break", "continue", "return", "try", "except", 
                    "finally", "raise", "assert", "with", "as", "yield", "from", "global", "nonlocal", "lambda", "pass"])
    #Group for 
    tokenGroups.append(["def", "class"])

    #Group for keywords
    tokenGroups.append(["and", "or", "not", "is", "in",])

    #Group for built in functions
    tokenGroups.append(["True", "False", "None"])


    tokenGroups.append(["(", ")", "[", "]", "{", "}", ])

    #Group for Import Statements
    tokenGroups.append(["import", "as", "with", "from",])

    #Group for libraries
    tokenGroups.append(["math", "numpy", "pandas", "tensorflow", "keras", "sklearn", "matplotlib", "seaborn",
                        "scipy", "statsmodels", "cv2", "pillow", "requests", "beautifulsoup4", "pyautogui", "pyperclip", 
                        "selenium", "openpyxl", "pytz", "pyinputplus", "logging", "multiprocessing", "threading", "time",
                        "datetime", "os", "shutil", "zipfile", "pathlib", "re", "random", "json", "csv", "webbrowser", "sys",
                        "pydoc", "copy", "pprint", "pycparser", "ctypes", "inspect", "operator", "itertools", "functools",
                        "collections", "gc", "weakref", "array", "types", "numbers", "decimal", "fractions", "statistics", 
                        "cmath", "timeit", "doctest", "unittest", "trace", "dis", "pickle", "profile", "cProfile", "time", 
                        "tracemalloc", "warnings", "contextlib", "abc", "atexit", "errno", "fcntl", "glob", "grp", "io", 
                        "logging", "multiprocessing", "operator", "os", "pkgutil", "pty", "pwd", "select", "signal", 
                        "socket", "spwd", "stat", "subprocess", "sys", "termios", "threading", "time", "tty", "urllib",
                        "uuid", "venv", "zipapp", "zipfile", "zlib", "argparse", "getopt", "logging", "optparse", 
                        "string", "textwrap", "cmd", "shlex",])
    #Group for datatypes
    tokenGroups.append(['str', 'int', ])
    #group for common data structure calls
    tokenGroups.append(["append", "remove", "format", "join", "value"])
    #group for common calls for data structures
    tokenGroups.append(["len", "isinstance"])

    #common var names that missed or skipped similarization
    tokenGroups.append(["x", "y", "i", "n"])





def main():
    args = parser.parse_args()
    input_file = args.input + "/tokenizer.json"
    output_file = args.output
    with open(input_file) as f:
        tokenizerModel = tokenizer_from_json(f.read())
    sortedWordIndex = sorted(tokenizerModel.word_index.items(), key=lambda kv: kv[1])
    #remove any values in tokenGroups
    initTokenGroups()
    for group in tokenGroups:
        for token in group:
            for i in range(len(sortedWordIndex)):
                if token == sortedWordIndex[i][0]:
                    sortedWordIndex.pop(i)
                    break

    #Print top 100
    print("Top 100")
    print(sortedWordIndex[:100])


if __name__ == '__main__':
    main()



