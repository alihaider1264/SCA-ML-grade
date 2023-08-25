from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import numpy as np
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
import re
import numpy as np
import pickle
from IPython.display import clear_output
import json

models = []
tokenizers = []
modelInfos = []
modelsDIR = "D:\\models\\python\\"
modelNames = ["python_model_1_IMPROVED", "python_model_1_Similar", "python_model_2_Similar"]
modelSimilarized = [False, True, False]
nextFileID = 0
grades = []

gradeDataFrame = pd.DataFrame()

import traceback
ERROR = ''

import ast
import autopep8

def change_names(code):
  #get the size of the code in memory
  size = sys.getsizeof(code)

  try:
    tree = ast.parse(code)
  except:
    #start on new thread to be able to time out
    code = autopep8.fix_code(code)
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
    elif isinstance(node, ast.arguments):
      #use same names for variables in function arguments
        for arg in node.args:
            if arg.arg not in names:
                new_name = f"var {var_count}"
                names[arg.arg] = new_name
                var_count += 1
                if (var_count > count_Limit):
                    var_count = 1
            arg.arg = names[arg.arg]
    

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


regexBlankLineMostly = r"(^\s{1,}$)"
regexBlankLineFinish = r"(^\n{1,})"

def stringProcessing(string, shouldSimilarize = False):
    if (not shouldSimilarize):
        string = string.replace("\"\"\"" , "\"")
        string = string.replace("\'\'\'" , "\"")
        string = string.replace("\\'" , "")
        string = string.replace('\\"' , "")
        string = re.sub("('|\")[\x1f-\x7e]{1,}?('|\")", " \"sGH\"", string)
        string = re.sub("#.*", "", string)
    else:
        string = change_names(string)
    string = string.replace('    ', '\t')
    string = re.sub(regexBlankLineMostly, '', string, 0, re.MULTILINE)
    string = re.sub(regexBlankLineFinish, '', string, 0, re.MULTILINE)
    return string


to_pad = ['\n', '\t', '\r', '(', ')', '[', ']', '{', '}', '<', '>', '!', '?', ',', '.', ':', ';', '`', '~', '@', '#', '$', '%', '^', '&', '*', '=', '+', '/', '\\', '|']

def stringPadding(dataSet):
    if (type(dataSet) == str):
        for i in range(len(to_pad)):
            dataSet = dataSet.replace(to_pad[i], ' ' + to_pad[i] + ' ')
        return dataSet



def gradeString(string):
    import traceback
    grades = []
    i = 0
    for model in models:
        try:
            stringtmp = string
            stringtmp = stringProcessing(stringtmp, modelSimilarized[i])
            stringtmp = stringPadding(stringtmp)


            stringtmp = tokenizers[i].texts_to_sequences([stringtmp])
            stringtmp = pad_sequences(stringtmp, maxlen=modelInfos[i]['maxLen'])
            print(stringtmp)
            grades.append(model.predict(stringtmp)[0][0])
            del(stringtmp)
        except:
            #pop up qt message box
            print("Error")
            grades.append(-1)
            global ERROR
            ERROR = traceback.format_exc()
        i += 1
    return grades
    

class Ui_MainWindow(object):
    def __init__(self):
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 630)
        
        self.tabWidgetMain = QtWidgets.QTabWidget(MainWindow)
        self.tabWidgetMain.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.tabWidgetMain.setObjectName("maintabWidget")
        
        self.maintab_1 = QtWidgets.QWidget()
        self.maintab_1.setObjectName("FileManagement")
        self.tabWidgetMain.addTab(self.maintab_1, "Individual File Analysis")
        

        self.pushButton = QtWidgets.QPushButton(self.maintab_1)
        self.pushButton.setGeometry(QtCore.QRect(10, 560, 311, 40))
        self.pushButton.setText("Add Files")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.addFiles)
        #Add a table on the left side of the window with a filename column and a grade column
        self.tableWidget = QtWidgets.QTableWidget(self.maintab_1)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 311, 550))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(150)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(150)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(30)
        self.tableWidget.verticalHeader().setMinimumSectionSize(30)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setCornerButtonEnabled(False)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(3)
        #hide last column
        self.tableWidget.setColumnHidden(2, True)
        self.tableWidget.setHorizontalHeaderLabels(["File Name", "Grade", "fileID"])
        #on selecting a file, show the contents of the file on the right side of the window
        self.tableWidget.itemSelectionChanged.connect(self.gradeTableItemSelectionChanged)
        self.rightSidesplitter = QtWidgets.QSplitter(self.maintab_1)
        self.rightSidesplitter.setGeometry(QtCore.QRect(330, 10, 461, 590))
        self.rightSidesplitter.setOrientation(QtCore.Qt.Vertical)
        self.rightSidesplitter.setObjectName("rightSidesplitter")
        #call rightSideSplitterResizeEvent when the splitter is moved
        self.rightSidesplitter.splitterMoved.connect(self.rightSideSplitterResized)
        #set up a text box on the top right of the window
        self.textEdit = QtWidgets.QTextEdit(self.rightSidesplitter)
        self.textEdit.setGeometry(QtCore.QRect(330, 10, 461, 481))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setReadOnly(True)
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        #Set up an even for when the text box is edited
        self.textEdit.textChanged.connect(self.editedCode)
        #set up a tabbed window on the bottom right of the window
        self.tabWidget = QtWidgets.QTabWidget(self.rightSidesplitter)
        self.tabWidget.setGeometry(QtCore.QRect(330, 490, 461, 100))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "modelInfo")
        self.modelInfoTable = QtWidgets.QTableWidget(self.tab)
        self.modelInfoTable.setGeometry(QtCore.QRect(0, 0, 461, 100))
        #make modelInfoTable scrollable
        self.modelInfoTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tokenInfo")
        self.tabWidget.addTab(self.tab_2, "Token View")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "Tab Group Analysis")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "Line Impact Analysis")
        #when tab2 is selected, show the tokenizer insight
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.upgradeGradeButton = QtWidgets.QPushButton(self.textEdit)
        #hide the upgrade grade button until the text box is edited
        self.upgradeGradeButton.setText("Update!")
        self.upgradeGradeButton.clicked.connect(self.updateGrade)
        #put in bottom right corner of text box
        self.upgradeGradeButton.move(self.textEdit.width() - self.upgradeGradeButton.width(), self.textEdit.height() - self.upgradeGradeButton.height())
        self.upgradeGradeButton.setObjectName("upgradeGradeButton")
        self.upgradeGradeButton.hide()
        self.tokenizerTabs = QtWidgets.QTabWidget(self.tab_2)
        self.tokenizerTabs.resize(461, 30)
        #when tab_2 is selected run the tokenizerTabsSelectionChanged function
        for i in range(len(tokenizers)):
            self.tokenizerTabs.addTab(QtWidgets.QWidget(), modelNames[i])
        #select the first tab by default
        self.tokenizerTabs.setCurrentIndex(0)
        self.tokenizerInfoText = QtWidgets.QTextEdit(self.tab_2)
        #move the tokenizerInfoText below the tabs
        self.tokenizerInfoText.move(0, 30)
        
        
        self.tokenizerTabs.currentChanged.connect(self.getTokenizedTranslation)

        #add a table to tab_3
        self.groupAnalysisTable = QtWidgets.QTableWidget(self.tab_3)
        self.groupAnalysisTable.setGeometry(QtCore.QRect(0, 0, 461, 100))
        #add a table to tab_4
        self.lineImpactTable = QtWidgets.QTableWidget(self.tab_4)
        self.lineImpactTable.setGeometry(QtCore.QRect(0, 0, 461, 100))
        
        
        

        
            
        #set up MainTab2
        self.maintab_2 = QtWidgets.QWidget()
        self.maintab_2.setObjectName("maintab_2")
        self.tabWidgetMain.addTab(self.maintab_2, "Group File Analysis")
        
        #set up MainTab3
        self.maintab_3 = QtWidgets.QWidget()
        self.maintab_3.setObjectName("maintab_3")
        self.tabWidgetMain.addTab(self.maintab_3, "Model Info")
        
        self.tabWidget_modelInfo = QtWidgets.QTabWidget(self.maintab_3)
        self.tabWidget_modelInfo.setGeometry(QtCore.QRect(0, 0, 800, 600))
        self.tabWidget_modelInfo.setObjectName("tabWidget_modelInfo")
        tabsForModelInfo = []
        for model in modelNames:
            tabsForModelInfo.append(QtWidgets.QWidget())
            self.tabWidget_modelInfo.addTab(tabsForModelInfo[-1], model)
        
        
        

        #MainTab2 Stuff
        #create another tab bar
        
        

        MainWindow.setCentralWidget(self.tabWidgetMain)


    
    def rightSideSplitterResized(self):
        self.upgradeGradeButton.move(self.textEdit.width() - self.upgradeGradeButton.width(), self.textEdit.height() - self.upgradeGradeButton.height())
        self.tokenizerInfoText.resize(self.tab_2.width(), self.tab_2.height() - 30)
        self.modelInfoTable.resize(self.tab.width(), self.tab.height())
        self.groupAnalysisTable.resize(self.tab_3.width(), self.tab_3.height())
        self.lineImpactTable.resize(self.tab_4.width(), self.tab_4.height())
    def tabChanged(self):
        if self.tabWidget.currentIndex() == 0:
            "todo"
        if self.tabWidget.currentIndex() == 1:
            self.getTokenizedTranslation()
    def addFiles(self):
        global nextFileID
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Python (*.py);;Text (*.txt)")
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            for fileName in fileNames: 
                fileID = nextFileID
                nextFileID = nextFileID + 1
                grades = gradeString(open(fileName, 'r').read())
                for i in range(len(grades)):
                    if grades[i] == -1:
                        #create pop up window
                        self.popUp = QtWidgets.QWidget()
                        self.popUp.resize(400, 200)
                        self.popUp.setWindowTitle("Grade Error")
                        
                        self.scrollArea = QtWidgets.QScrollArea(self.popUp)
                        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 400, 200))
                        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
                        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
                        
                        self.popUpLabel = QtWidgets.QLabel(self.scrollArea)
                        self.popUpLabel.setText("The grading for " + fileName + " has encountered an error. Please make sure that the code contains no syntax errors and that the code is formatted correctly. \n \n Console output: \n" + ERROR) 
                        self.popUp.show()
                        #enable scrolling of the text
                        self.popUpLabel.setWordWrap(False)
                        
                print (fileName)
                tempDF = pd.DataFrame([[fileName, grades, fileID]], columns = ['fileName', 'grades', 'fileID'])
                global gradeDataFrame
                gradeDataFrame = pd.concat([gradeDataFrame, tempDF])
                

                print (gradeDataFrame)
                if grades == 0:
                    avgGrade = "N/A"
                else:
                    avgGrade = str(np.mean(grades))
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(fileName.split("/")[-1]))
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(avgGrade))
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(str(fileID)))
                
    def gradeTableItemSelectionChanged(self):
        fileID = int(self.tableWidget.item(self.tableWidget.currentRow(), 2).text())
        #find the path in the dataframe using the fileID
        path = gradeDataFrame[gradeDataFrame['fileID'] == fileID]['fileName'].iloc[0]
        with open(path, "r") as f:
            self.textEdit.setText(f.read())
        f.close()
        self.modelInfoTable.clear()
        self.modelInfoTable.setRowCount(0)
        self.modelInfoTable.setColumnCount(3)
        self.modelInfoTable.setHorizontalHeaderLabels(["Model", "Grade", "Edited Grade"])
        print (self.tableWidget.currentRow())
        print("file ID is " + self.tableWidget.item(self.tableWidget.currentRow(), 2).text())

        for i in range(len(modelNames)):
            self.modelInfoTable.insertRow(self.modelInfoTable.rowCount())
            self.modelInfoTable.setItem(self.modelInfoTable.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(modelNames[i]))
            #search for the correct grades using the fileID
            self.modelInfoTable.setItem(self.modelInfoTable.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(gradeDataFrame.loc[gradeDataFrame['fileID'] == int(self.tableWidget.item(self.tableWidget.currentRow(), 2).text())].iloc[0,1][i])))
        self.modelInfoTable.hideColumn(2)
        self.modelInfoTable.resizeColumnsToContents()
        self.textEdit.setReadOnly(False)
        self.upgradeGradeButton.hide()
        if (self.tabWidget.currentIndex() == 1):
            self.getTokenizedTranslation()

        
        
    def editedCode(self):
        self.upgradeGradeButton.show()        
        
    def updateGrade(self):
        if self.tabWidget.currentIndex() == 0:
            self.modelInfoTable.showColumn(2)
            self.modelInfoTable.resizeColumnsToContents()
            grades = gradeString(self.textEdit.toPlainText())
            
            for i in range(len(grades)):
                if grades[i] == -1:
                    #create pop up window
                    self.popUp = QtWidgets.QWidget()
                    self.popUp.resize(400, 200)
                    self.popUp.setWindowTitle("Grade Error")
                    self.popUpLabel = QtWidgets.QLabel(self.popUp)
                    self.popUpLabel.setText("The grading for your edit has encountered an error. Please make sure that the code contains no syntax errors and that the code is formatted correctly.")
                    self.popUp.show()
            
            #grades is an array, update column 2 with the new grades
            for i in range(len(grades)):
                self.modelInfoTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(grades[i])))
                
            #compare column 1 and column 2 and make green for a positive delta and red for a negative delta
            for i in range(len(grades)):
                if float(self.modelInfoTable.item(i, 1).text()) < float(self.modelInfoTable.item(i, 2).text()):
                    self.modelInfoTable.item(i, 2).setBackground(QtGui.QColor(0,255,0))
                elif float(self.modelInfoTable.item(i, 1).text()) > float(self.modelInfoTable.item(i, 2).text()):
                    self.modelInfoTable.item(i, 2).setBackground(QtGui.QColor(255,0,0))
                else:
                    self.modelInfoTable.item(i, 2).setBackground(QtGui.QColor(255,255,255))
                    
            self.upgradeGradeButton.hide()
        elif self.tabWidget.currentIndex() == 1:
            self.getTokenizedTranslation()

    def getTokenizedTranslation(self):
        #get the code from the text box
        code = self.textEdit.toPlainText()
        #get the current tab
        currentTab = self.tokenizerTabs.currentIndex()
        #get the current text
        currentText = self.textEdit.toPlainText()
        #get the current tokenizer
        currentTokenizer = tokenizers[currentTab]
        try:
            code = stringProcessing(code, modelSimilarized[currentTab])
            print(modelSimilarized[currentTab])
            code = stringPadding(code)
            #tokenize the code
            code = currentTokenizer.texts_to_sequences([code])
            code = currentTokenizer.sequences_to_texts(code)
            
            print (code)
            self.tokenizerInfoText.setText(str(code))
            self.tokenizerInfoText.setReadOnly(True)
            #Properly format the text
            x = str(code)
            x = x.replace("\\'numlit\\'", "numlit")
            x = x.replace("[", "")
            x = x.replace("]", "")
            x = x.replace("'", "")
            x = x.replace(",", "")
            x = x.replace("\\n ", "\n")
            x = x.replace("\\t ", "\t")
            x = x.replace("\\n", "\n")
            x = x.replace("\\t", "\t")
            self.tokenizerInfoText.setTabStopWidth(8)
            self.tokenizerInfoText.setText(self.tokenizerInfoText.toPlainText() + "\n\n\n" + x)
        except:
            self.tokenizerInfoText.setText("Error tokenizing code, please check that the code is compiable")

        


def modelLoader():
    for modelName in modelNames:
        model = load_model(modelsDIR + modelName + '/model.h5')
        print(model.summary())
        models.append(model)
        with open(modelsDIR + modelName + '/tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)
            tokenizers.append(tokenizer)
        with open(modelsDIR + modelName + '/modelInfo.json') as json_file:
            modelInfo = json.load(json_file)
            #add the model name
            modelInfo = {**modelInfo, **{"modelName": modelName}}
            modelInfos.append(modelInfo)
            
            
            
            


def window():
    try:
        modelLoader()
    except:
        print("Error loading models")
        return
    app = QtWidgets.QApplication(sys.argv)
    win = Ui_MainWindow()
    win.MainWindow.show()
    
    sys.exit(app.exec_())
    
    
window()