import numpy as np
import pandas as pd
import os
import tensorflow as tf
import keras
import argparse

#This will take a dataframe of tokens and apply the catigories to them

#inputs, Dictionary of tokens and their catigories, dataframe of tokens
#output, dataframe of tokens with catigories


parser = argparse.ArgumentParser(description='Token Category Generator')

parser.add_argument('-i', '--input', type=str, required=True,
                    help='Input file path')
parser.add_argument('-o', '--output', type=str, required=False,
                    help='Output file path')


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def translateTokens(tokenDict, tokenDf):
    translatedDF = pd.DataFrame(columns=['tokenGroupCode', 'Path'])
    for i in range(len(tokenDf)):
        printProgressBar(i + 1, len(tokenDf), prefix = 'Progressing:', suffix = 'Complete', length = 50)
        tempTokenArray = []
        for j in tokenDf['tokenCode'][i]:
            tempTokenArray.append(tokenDict[j])
        tempTokenArray = np.array(tempTokenArray)
        translatedDF = pd.concat([translatedDF, pd.DataFrame({'tokenGroupCode': [tempTokenArray], 'Path': [tokenDf['Path'][i]]})], ignore_index=True)
    return translatedDF



#for testing
def main():
    argparse = parser.parse_args()
    tokenDict = np.load(argparse.input + "/GroupDict.npy", allow_pickle=True).item()
    tokenDf = pd.read_pickle(argparse.input + "/tokenizedData.pkl")
    translatedDF = translateTokens(tokenDict, tokenDf)
    #save the dataframe
    translatedDF.to_pickle(argparse.output+ "/tokenGroupDataframe.pkl")

if __name__ == '__main__':
    main()

        