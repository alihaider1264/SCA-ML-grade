#take input folder and output folder as arguments

import argparse
import json
import warnings

parser = argparse.ArgumentParser(description='Input a Grade Downloader folder, and this will generate grades for each file')
parser.add_argument('-i', '--input', help='The input folder', required=True)
parser.add_argument('-o', '--output', help='The output folder', required=True)

# Print iterations progress
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

def searchFiles(path, fileformats):
    filesToDo = []
    for root, dirs, files in os.walk(path):
        for file in files:
            for fileformat in fileformats:
                if file.endswith(fileformat):
                    #code to generate a list of paths of files to generate logs for
                    filesToDo.append(os.path.join(root, file).split(path)[1])
    return filesToDo

def searchFileName(path, fileName):
    filesToDo = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == fileName:
                #code to generate a list of paths of files to generate logs for
                filesToDo.append(os.path.join(root, file).split(path)[1])
    return filesToDo
def main():
    gitInfoDatabase = null
    if 




    #Generate a list of files to index
    #filesToIndex = searchFileName(pathToDataCollectorDatabase,"gitinfo.txt")
    #Instead of searching for files, get a 1 level list of directories
    filesToIndex = [name for name in os.listdir(pathToDataCollectorDatabase) if os.path.isdir(os.path.join(pathToDataCollectorDatabase, name))]
    #Create a dataframe that contains the data of the gitinfo.txt files
    warnings.filterwarnings('ignore')
    i=0
    #example of the gitinfo.txt file    {"id": 3452233, "name": "hjlebbink/asm-dude", "isFork": false, "commits": 939, "branches": 8, "defaultBranch": "master", "releases": 39, "contributors": 10, "license": "MIT License", "watchers": 762, "stargazers": 3906, "forks": 76, "size": 82262, "createdAt": "2016-02-19 03:43:23", "pushedAt": "2022-01-06 01:33:34", "updatedAt": "2022-01-08 08:02:49", "homepage": "", "mainLanguage": "Python", "totalIssues": 118, "openIssues": 32, "totalPullRequests": 13, "openPullRequests": 1, "lastCommit": "2021-12-07 08:47:07", "lastCommitSHA": "1e1e3dc2364e8ed549ba404868b6473ba435b25c", "hasWiki": true, "isArchived": false, "languages": {"Python": 4274689, "C#": 2554588, "C": 1311140, "C++": 644077, "Assembly": 164163, "Shell": 2764, "Go": 1779, "Batchfile": 410}, "labels": ["bug", "duplicate", "enhancement", "help wanted", "invalid", "question", "wontfix"]}
    df = pd.DataFrame(columns=['id', 'name', 'isFork', 'commits', 'branches', 'defaultBranch', 'releases', 'contributors', 'license', 'watchers', 'stargazers', 'forks', 'size', 'createdAt', 'pushedAt', 'updatedAt', 'homepage', 'mainLanguage', 'totalIssues', 'openIssues', 'totalPullRequests', 'openPullRequests', 'lastCommit', 'lastCommitSHA', 'hasWiki', 'isArchived', 'languages', 'labels' , 'path'])
    for folder in filesToIndex:
        #print progress bar
        printProgressBar(i, len(filesToIndex), prefix = 'Progress:', suffix = 'Complete', length = 50)
        try:
            with open(pathToDataCollectorDatabase + slashForDir + folder + slashForDir + "gitinfo.txt", 'r') as f:
                d = json.load(f)
                f.close()
                dftemp = pd.json_normalize(d)
                dftemp['path'] = folder
                df = pd.concat([df, dftemp], ignore_index=True)
        except:
            print("Error with folder: " + folder)
        i = i+1


