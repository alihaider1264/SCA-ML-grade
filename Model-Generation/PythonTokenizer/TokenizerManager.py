import argparse
import SupportingClasses.CaMlSupportingClasses as mcall
import SupportingClasses.PythonProcessing as textProcessing
import os
import pandas as pd
import datetime

from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences

maxWords = 10000

parser = argparse.ArgumentParser(description='Input a Grade Downloader folder, and this will generate grades for each file')
parser.add_argument('-i', '--input', help='The input folder', required=True)
parser.add_argument('-o', '--output', help='The output folder', required=False)
parser.add_argument('-d', '--dateAsFName', help='Make the output folder a subfolder and have the date as the name', required = False,  action="store_true")

def generateTokenizer(input):
    tokenizer = Tokenizer(filters='' , split=' ', lower=True, num_words=maxWords)
    tokenizer.fit_on_texts(input) 
    return tokenizer


def tokenStart(inputFolder, outputFolder, dateAsFileName):
    filesToIndex = [name for name in os.listdir(inputFolder) if os.path.isdir(os.path.join(inputFolder, name))]
    #Let's assume all of the folders are in the correct format for now
    #TODO: Add a check to make sure the folders are in the correct format
    filesToIndex = mcall.searchFiles(inputFolder, [".txt"], 'gitinfo.txt')

    df = pd.DataFrame(columns=['tokenCode', 'Path'])
    #TODO: Make Multithreaded
    #File Processing in preperation for tokenization
    print(filesToIndex)
    for i in range(len(filesToIndex)):
        #open the file
        with open(inputFolder + filesToIndex[i], 'r', encoding="utf8") as file:
            #read the file
            data = file.read()
            #tokenize the file
            processedCode = textProcessing.tokenizePythonString(data)
            #add the tokens to the dataframe not using append
            if processedCode != '':
                newData = {'tokenCode': processedCode, 'Path': filesToIndex[i]}
                df = pd.concat([df, pd.DataFrame(newData, index=[0])], ignore_index=True)

        #print the progress bar
        mcall.printProgressBar(i + 1, len(filesToIndex), prefix = 'Progress:', suffix = 'Complete', length = 50)
    tokenizer = generateTokenizer(df['tokenCode'])
    df['tokenCode'] = tokenizer.texts_to_sequences(df['tokenCode'])

    doOutput = outputFolder != None

    if doOutput:
        if dateAsFileName:
            outputFolder = os.path.join(outputFolder, datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        df.to_pickle(os.path.join(outputFolder, 'tokenizedData.pkl'))
        jsonToken = tokenizer.to_json()
        with open(os.path.join(outputFolder, 'tokenizer.json'), 'w', encoding="utf8") as file:
            file.write(jsonToken)
            file.close()
    else :
        print(df)
        print(tokenizer)

def main():
    args = parser.parse_args()
    tokenStart(args.input, args.output, args.dateAsFName)
    
main()


