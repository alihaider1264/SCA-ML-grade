#Goal: Reduce the variation between code by removing all variable names and replacing them 
    #with generic but still unique names
#Input= str of python code (With Args if you want)
#Output = str of similarized python code

from numbers import Number
import autopep8
import ast
import sys

def change_names(code, lengthLimitmb = .05, enableLengthLimit = True, autopep8FixTimeLimit = 10, skipErrorCorrection = False):
  lengthLimitBytes = lengthLimitmb * 1000000
  #get the size of the code in memory
  size = sys.getsizeof(code)

  if (skipErrorCorrection == True or (enableLengthLimit and size > lengthLimitBytes)):
    try:
      tree = ast.parse(code)
    except:
      return ''
  else:
    try:
      tree = ast.parse(code)
    except:
      try:
        #TODO: start on new thread to be able to time out
        code = autopep8.fix_code(code, options={"max_line_length": 500, "aggressive": 2})
        tree = ast.parse(code)
      except:
        return ''
    

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
            new_name = f"var1 {var_count}"
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
        new_name = f"class1 {class_count}"
        names[node.name] = new_name
        class_count += 1
        if (class_count > count_Limit):
          class_count = 1
      node.name = names[node.name]
    elif isinstance(node, ast.FunctionDef):
      if node.name not in names:
        new_name = f"funct1 {funct_count}"
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