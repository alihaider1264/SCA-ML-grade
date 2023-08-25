#Goal: To add space between characters, reduce redundent newlines and make tabs tokens


#Input str of python code in pep8 format(Plus args if you want)
#Output str of spaced out and normalized python code.


#pep8 due to the 4 space tabs. TODO: It's possible to autodetect this by reading lines 
    #on the first and 2nd level and getting the amount of spaces between them. 
    # (Or just using the first indented line value).
    # A better implimentation would be to parse the level for each line and 
    # just make the tab symbol corilate to the level of a line

import re

regexBlankLineMostly = r"(^\s{1,}$)"
regexBlankLineFinish = r"(^\n{1,})"

def stringProcessing(stringText):
    stringText = stringText.replace('    ', '\t')
    stringText = re.sub(regexBlankLineMostly, '', stringText, 0, re.MULTILINE)
    stringText = re.sub(regexBlankLineFinish, '', stringText, 0, re.MULTILINE)
    return stringText

to_pad = ['\n', '\t', '\r', '(', ')', '[', ']', '{', '}', '<', '>', '!', '?', ',', '.', ':', ';', '`', '~', '@', '#', '$', '%', '^', '&', '*', '=', '+', '/', '\\', '|']

def stringPadding(dataSet):
    if (type(dataSet) == str):
        for i in range(len(to_pad)):
            dataSet = dataSet.replace(to_pad[i], ' ' + to_pad[i] + ' ')
        return dataSet

def processCodeString(codeString):
    return(stringPadding(stringProcessing(codeString)))