""" OUTLINE
As an input folder, this program expects a folder made with the data parsing utility in this repository. 
This will create folders inside a repository to represent each source file, and inside each folder will be a complete source representation of the file after every commit in a .txt format.
These files will be named by the order in which the commit was commited. 
The first file will be the original file, and the last file will be the most recent commit.
There will also be a corisponding JSON files with the same file name as the source file, but with a .json extension.
This JSON file will contain the commit information for the commit that the source file was created from.
This application will run the data processing required and then
generate a grade using a NN which was inputed as an argument.
It will then save the grades in this structure:
Each folder will have a grade file. 
for each file in a folder, there will be a line in the grade file
The first characters will be the file name without the extension, 
It will then be followed by a space and then the grade.
The folder structure of the output will be the same as the input, but in a different location.



"""
#TODO, when we have the data processing in library form, we will need to import it here and rework the function calls.

from numbers import Number
import autopep8
import os
import argparse
import ast
import sys
import re
import pickle
from keras.utils import pad_sequences
import numpy as np
from keras.models import load_model
import json
import subprocess
import multiprocessing



#Idealy we would want to use a file which contains the processing required as a library, but it is stuck in a Jupyter Notebook for now. 
slashForDir = "\\"
multiRepoFolder = False

#MODEL OPTIONS
noSimilarization = False

#CODE SIMILARIZATION CONFIG VALUES
skipErrorCorrection = True
lengthLimitmb = .05
lengthLimitBytes = lengthLimitmb * 1000000
enableLengthLimit = True
autopep8FixTimeLimit = 10 #seconds
class gradeType:
    fileName : str
    grade : Number
    
    
class modelWithEverythingNeeded:
    model : load_model
    tokenizer : pickle
    modelInfo : json
    
    
    
    
def searchFileFormat(path, fileformats):
    filesToDo = []
    for root, dirs, files in os.walk(path):
        for file in files:
            for fileformat in fileformats:
                if file.endswith(fileformat):
                    #code to generate a list of paths of files to generate logs for
                    filesToDo.append(os.path.join(root, file).split(path)[1])
    return filesToDo
def pythonProcessing(inputString):
    regexBlankLineMostly = r"(^\s{1,}$)"
    regexBlankLineFinish = r"(^\n{1,})"
    """stuff for later"""
    inputString = change_names(inputString)
    if (noSimilarization):
        inputString = inputString.replace("\"\"\"" , "\"")
        inputString = inputString.replace("\'\'\'" , "\"")
        inputString = inputString.replace("\\'" , "")
        inputString = inputString.replace('\\"' , "")
        inputString = re.sub("('|\")[\x1f-\x7e]{1,}?('|\")", " \"sGH\"", inputString)
        inputString = re.sub("#.*", "", inputString)
    inputString = inputString.replace('    ', '\t')
    inputString = re.sub(regexBlankLineMostly, '', inputString, 0, re.MULTILINE)
    inputString = re.sub(regexBlankLineFinish, '', inputString, 0, re.MULTILINE)
    return inputString
def pythonTokenizing(inputString , modelWInfo):
    tokens = modelWInfo.tokenizer.texts_to_sequences([inputString])
    tokens = pad_sequences(tokens, modelWInfo.modelInfo['maxLen'])
    return tokens
def pythonPadding(dataSet, to_pad = ['\n', '\t', '\r', '(', ')', '[', ']', '{', '}', '<', '>', '!', '?', ',', '.', ':', ';', '`', '~', '@', '#', '$', '%', '^', '&', '*', '=', '+', '/', '\\', '|']):
    #tokenize dataSet
    #dataSet = padSymbols(dataSet)
    
    #get rid of excess \n
    #pad to_pad segments with spaces in dataSet
    if (type(dataSet) == str):
        for i in range(len(to_pad)):
            dataSet = dataSet.replace(to_pad[i], ' ' + to_pad[i] + ' ')
        return dataSet
def change_names(code):
  #get the size of the code in memory
  size = sys.getsizeof(code)

  if (skipErrorCorrection == True or (enableLengthLimit and size > lengthLimitBytes)):
    tree = ast.parse(code)
  else:
    try:
      tree = ast.parse(code)
    except:
      #start on new thread to be able to time out
      
      code = autopep8.fix_code(code, options={"max_line_length": 500, "aggressive": 2})
      tree = ast.parse(code)
    

  names = {}

  var_count = 1
  class_count = 1
  funct_count = 1
  
  count_Limit = 100
  #If count_Limit is reached we will loop back to 1  

  for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
      for target in node.targets:
        if isinstance(target, ast.Name):
          if target.id not in names:
            new_name = f"var {var_count}"
            names[target.id] = new_name
            var_count += 1
            if (var_count > count_Limit):
              var_count = 1
          target.id = names[target.id]
    elif isinstance(node, ast.Name):
      if node.id in names:
        node.id = names[node.id]
    elif isinstance(node, ast.ClassDef):
      if node.name not in names:
        new_name = f"class {class_count}"
        names[node.name] = new_name
        class_count += 1
        if (class_count > count_Limit):
          class_count = 1
      node.name = names[node.name]
    elif isinstance(node, ast.FunctionDef):
      if node.name not in names:
        new_name = f"funct {funct_count}"
        names[node.name] = new_name
        funct_count += 1
        if (funct_count > count_Limit):
          funct_count = 1
      node.name = names[node.name]
    # Add this block to rename calls to the class methods
    elif isinstance(node, ast.Call):
      if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in names:
        node.func.value.id = names[node.func.value.id]
        #node.func.attr = names[node.func.attr]
      # Add this block to rename calls to functions defined inside the class
      elif isinstance(node.func, ast.Name) and node.func.id in names:
        node.func.id = names[node.func.id]
    # Add this block to rename attributes in method calls
    if isinstance(node, ast.Attribute) and node.attr in names:
      node.attr = names[node.attr]
    # Add this block to replace string literals
    elif isinstance(node, ast.Str):
      node.s = "strLit"
    # Add this block to replace number literals
    elif isinstance(node, ast.Num):
      node.n = "numLit"

  new_code = ast.unparse(tree)
  
  #make all """strLit""" into "strLit"
  new_code = new_code.replace('"""strLit"""', '"strLit"')
  #make all '''strLit''' into 'strLit'
  new_code = new_code.replace("'''strLit'''", "'strLit'")
  #make all 'strLit' into "strLit"
  new_code = new_code.replace("'strLit'", '"strLit"')
  
  

  return new_code
def findFoldersToGrade(path,multiRepo):
    folders = []
    folderToSearch = []
    
    if multiRepo:
        for files in os.listdir(path):
            if os.path.isdir(os.path.join(path, files)):
                if (os.path.isdir(os.path.join(path, files, "parsed"))):
                    folderToSearch.append(path + slashForDir +  files)
    else: 
        folderToSearch.append(path)
    for folder in folderToSearch:
      for root, dirs, files in os.walk(folder+slashForDir+"parsed"):
          if (root != path+slashForDir+"parsed"):
              for name in dirs:
                      if (multiRepo): #hacky fix for multiRepo, fix later
                        unwantedFolders = os.listdir(path + slashForDir + folder.split(slashForDir)[-1]+ slashForDir + "parsed")
                        if (name in unwantedFolders):
                          continue
                      folders.append(os.path.join(root, name))
    return folders
def gradeFolder(path, modelWInfo):
    grades = []
    #will be searching for .txt files
    for file in searchFileFormat(path, [".txt"]):
        newGrade = gradeType()
        try:
            newGrade.grade = gradeFile(path + file, modelWInfo)
            newGrade.fileName = file.split(".")[0]
            grades.append(newGrade)
        except:
            print("skipped file")
    #sort by file name number
    grades.sort(key=lambda x: int(x.fileName.split(slashForDir)[-1]))
    return grades
    
        
def gradeFile(path, modelWInfo):
    tokens = pythonTokenizing(pythonPadding(pythonProcessing(readFile(path))), modelWInfo)
    gradeValue = modelWInfo.model.predict(tokens).tolist()[0][0]
    return gradeValue
def readFile(path):
    file = open(path, "r")
    filecontents = file.read()
    file.close()
    return filecontents

def main():
    parser = argparse.ArgumentParser(description='A grading utility for testing, please open the source file and read Outline for more info.')
    parser.add_argument('-p', '--path', help='The path to the repository to run grades on. Please make this the folder with data already parsed into seperet files. By default this is the "Parsed" folder for a repository.', required=True)
    parser.add_argument('-o', '--output', help='The path to the output folder.', required=True)
    parser.add_argument('-m', '--model', help='The path to the model folder.', required=True)
    pathToModel = parser.parse_args().model
    multiRepoFolder = not os.path.exists(parser.parse_args().path + slashForDir + 'parsed')
    print (multiRepoFolder)
    
    
    #load tokenizer
    with open(pathToModel + slashForDir + 'tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    
    #load model
    model = load_model(pathToModel + slashForDir + 'model.h5')
    
    #load model info 
    with open(pathToModel + slashForDir + 'modelInfo.json') as json_file:
        modelInfo = json.load(json_file)
        
    folderToGrade = findFoldersToGrade(parser.parse_args().path, multiRepoFolder)

    
    modelWInfo = modelWithEverythingNeeded()
    modelWInfo.model = model
    modelWInfo.tokenizer = tokenizer
    modelWInfo.modelInfo = modelInfo
    for folder in folderToGrade:
      grade = gradeFolder(folder, modelWInfo)
      if (len(grade) > 1):
        #main loop of the program
        #write to file
        #create folder if it does not exist
        reponame = folder.split("parsed" + slashForDir)[0].split(slashForDir)[-2]
        dirString = parser.parse_args().output + slashForDir + reponame + slashForDir +  folder.split("parsed" + slashForDir)[1]
        print (dirString + "\n")
        if not os.path.exists(dirString):
            os.makedirs(dirString)
        
        file = open(dirString + slashForDir + folder.split(slashForDir)[-1] + ".txt", "w")

        #file = open(parser.parse_args().output + slashForDir + folder.split(slashForDir)[-2] + ".txt", "w")
        for gradeValue in grade:
            file.write(gradeValue.fileName + "|" + str(gradeValue.grade) + "\n")
        file.close()
        
        
        
        
main()