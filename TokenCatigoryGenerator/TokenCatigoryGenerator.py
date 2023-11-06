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
    global tokenGroups
    #Group for numbers 1 through 100 as strings
    numbArray = []
    for i in range(1, 101):
        numbArray.append(str(i))
    tokenGroups.append(numbArray)
    #Group for Literals
    tokenGroups.append(['strlit', "numlit", 
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
    tokenGroups.append(["def", "class", "self"])

    #Group for keywords
    tokenGroups.append(["and", "or", "not", "is", "in",])

    #Group for static values
    tokenGroups.append(["True", "False", "None", "true", "false", "none"])


    tokenGroups.append(["(", ")", "[", "]", "{", "}", "\\t" , "\'", "'''"])

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
    initTokenGroups()
    args = parser.parse_args()
    input_file = args.input + "/tokenizer.json"
    output_file = args.output
    with open(input_file) as f:
        tokenizerModel = tokenizer_from_json(f.read())

    initilizeTokenTranslation(tokenizerModel)
    exit()
    sortedWordIndex = sorted(tokenizerModel.word_index.items(), key=lambda kv: kv[1])
    #remove any values in tokenGroups
    initTokenGroups()
    for group in tokenGroups:
        for token in group:
            for i in range(len(sortedWordIndex)):
                if token == sortedWordIndex[i][0]:
                    sortedWordIndex.pop(i)
                    break

def initilizeTokenTranslation(tokenizer):
    tokenTranslation = []
    test = []
    fullTokenSequence = []
    for i in range(1, tokenizer.num_words):
        test.append(i)
        tokenTranslation.append(len(tokenGroups))

    #make test into a numpy array
    test = np.array(test)
    print (test)

    #the index will equal a token value, the value at the index will represent the catigory
    fullTokenSequence = str(tokenizer.sequences_to_texts([test]))
    print (fullTokenSequence)

    fullTokenSequence = fullTokenSequence[2:-2]
    fullTokenSequence = fullTokenSequence.split(" ")

    #split the string into a list
    print (fullTokenSequence)
    
    for i in range(len(tokenTranslation)):
        #see if the token is in the tokenGroups
        for j in range(len(tokenGroups)):
            if fullTokenSequence[i] in tokenGroups[j]:
                tokenTranslation[i] = j
                break

    print (tokenTranslation)
    print (fullTokenSequence[2])
    
    
    



if __name__ == '__main__':
    main()



