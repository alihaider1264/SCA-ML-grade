#take input folder and output folder as arguments
import argparse
import SupportingClasses.CaMlSupportingClasses as mcall
import os
import pandas as pd
import datetime
import datetime
import numpy as np
import json
import threading as th
import time
import sys


#commit comment keywords for code grade adjustment
positiveKeyWords = ['fix', 'resolve', 'resolve', 'resolved', 'resolves', 'resolving', 'close', 'closed', 'closes', 'closing', 'fixes', 'fixed', 'fixing', 'patch', 'patched', 'patching', 'update', 'updated', 'updating', 'upgrade', 'upgraded', 'upgrading', 'improve', 'improved', 'improving', 'improvement', 'improvements', 'improves', 'improving', 'enhance', 'enhanced', 'enhances', 'enhancing', 'enhancement', 'enhancements']
positiveKeyWordsBigImpact = ['Signed-off', 'Merge', 'Merged']
positiveKeyWordsValue = 1
positiveKeyWordsBigImpactValue = 5
negitiveKeyWords = ['todo','tofix','bugged','fix me','fix-me']
negitiveKeyWordsValue = -1

threads = 16

prevCommitScoreAdjustmentNegitiveKeyWords = ['revert','reverted','reverting','reverts']
prevCommitScoreAdjustmentNegitiveKeyWordsValue = -10
df = pd.DataFrame(columns=['fileGrade', 'Path'])

inputFolder,outputFolder = "",""
parser = argparse.ArgumentParser(description='Input a Grade Downloader folder, and this will generate grades for each file')
parser.add_argument('-i', '--input', help='The input folder', required=True)
parser.add_argument('-o', '--output', help='The output folder', required=False)
def getSubFolders(path):
    return([name for name in os.listdir(inputFolder) if os.path.isdir(os.path.join(inputFolder, name)) and name != "git"])

def getFiles(foldersToProcess):
    filesToIndex = []
    for folder in foldersToProcess:
        filesToIndex.append(mcall.searchFileName(os.path.join(inputFolder,folder), "0.py"))
    return filesToIndex

def getGitInfo(gitInfoPath):
    with open(os.path.join(gitInfoPath,"git.info"), 'r', encoding="utf8") as file:
        data = file.read()
        return data

#This expects a folder full of .py files and .json files with files names corisponding to numbers such as 0,1,2
#If there's missing files we expect them to be because of duplicates or the file getting deleted at some point
def getFilesToGradeFromRevisionFolder(FolderPath, codeExtension = ".py", jsonExtension = ".json"):
    #check to see if it's a dir or a file, if it's a file strip it
    if (os.path.isfile(FolderPath)):
        FolderPath = FolderPath.split("0.py")[0]
    #List the files in a directory
    filesToGradeList = []
    deletedFile = False
    try:
        allFiles = os.listdir(FolderPath)
    except:
        return filesToGradeList
    fileCount = len(allFiles)
    #check to see if it's odd
    if len(allFiles) % 2 != 0:
        fileCount = fileCount - 1
        deletedFile = True
    fileCount = int(fileCount / 2)
    for i in range(fileCount):
        if (os.path.exists(os.path.join(FolderPath, str(i) + codeExtension)) and os.path.exists(os.path.join(FolderPath, str(i) + jsonExtension))):
            filesToGradeList.append([os.path.join(FolderPath, str(i) + codeExtension), os.path.join(FolderPath, str(i) + jsonExtension)])
    if (deletedFile):
        filesToGradeList.append(["DELETED", "DELETED"])
    return filesToGradeList

def baseRepositoryGrading(repoInfo):
    #Example {"id": 3584343, "name": "davebshow/goblin", "isFork": false, "commits": 363, "branches": 31, "defaultBranch": "master", "releases": 0, "contributors": 8, "license": "Other", "watchers": 13, "stargazers": 90, "forks": 21, "size": 487, "createdAt": "2016-07-01 05:59:12", "pushedAt": "2018-11-06 01:10:31", "updatedAt": "2020-12-04 09:55:15", "homepage": "", "mainLanguage": "Python", "totalIssues": 64, "openIssues": 15, "totalPullRequests": 48, "openPullRequests": 2, "lastCommit": "2018-08-29 04:16:23", "lastCommitSHA": "ab6966eafd4a5de9d60a1d88f2054f5104dba241", "hasWiki": true, "isArchived": false, "languages": {}, "labels": []}
    repoBaseScore = 0
    #subtract the dates from creation date and last updated date to get an age score
    #'%Y-%m-%d T%H:%M:%SZ'
    repoAge = (datetime.datetime.strptime(repoInfo['updatedAt'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(repoInfo['createdAt'], '%Y-%m-%d %H:%M:%S'))
    repoAge = repoAge.days
    #The older the repo the higher the score
    ageScore = 200 - (repoAge/365)*100
    #add a score based on the number of contributors
    contributorRepoScore = repoInfo['contributors']*5
    #add a score based on the number of stars
    starScore = repoInfo['stargazers'] * 10
    #add a score based on the number of forks
    forkScore = repoInfo['forks'] * 10
    #add a score based on the number of watchers
    watchScore = repoInfo['watchers'] * 10
    #add a score based on the number of issues
    repoBaseScore = repoBaseScore + (repoInfo['totalIssues'] * 10)
    totIssues = repoInfo['totalIssues']
    opIssues = repoInfo['openIssues']
    if (opIssues != 0):
        issuesScore = 90 - (totIssues/opIssues)*100
    else:
        issuesScore = -1
    top2Scores = sorted([ageScore, contributorRepoScore, starScore, forkScore, watchScore, issuesScore], reverse=True)[:2]
    #add the top 2 scores together
    repoBaseScore = repoBaseScore + top2Scores[0] + top2Scores[1]
    repoBaseScore = repoBaseScore/50
    if (issuesScore == -1):
        repoBaseScore = repoBaseScore -15
    return repoBaseScore
    
def commitFolderGrading (filesToGradeList, repoBaseScore):
    global df
    #filesToGradeList is formatted as [code path, json path]
    numberOfCommits = len(filesToGradeList)
    commitGrade = []
    for i in range(len(filesToGradeList)):
        #get files
        commitinfo = ''
        currentJSONFilePath = filesToGradeList[i][1]
        if (currentJSONFilePath == "DELETED"):
            continue
        try:
            with open(filesToGradeList[i][1], 'r', encoding="utf8") as file:
                commitinfo = json.loads(file.read())
        except:
            continue

        #get the number of contributors
        #Formatting = "msg": "UI vision refactor (#2115)\n\n* refactor vision\r\n\r\n* don't show slow frame message when in preview mode\r\n\r\n* change draws to uint32_t\r\n\r\n* set vision_seen=false after destroy\r\n\r\n* remove vision_connect_thread\r\n\r\n* refactor ui_update\r\n\r\n* seelp 30ms when vision is not connected\r\n\r\n* remove should_swap\r\n\r\n* call ui_update_sizes before ui_draw\r\n\r\n* rebase\r\n\r\n* start bigger UI refactor\r\n\r\n* don't need the touch fd\r\n\r\n* fix qt build\r\n\r\n* more cleanup\r\n\r\n* more responsive\r\n\r\n* more refactor\r\n\r\n* fix for pc\r\n\r\n* poll for frames\r\n\r\n* lower CPU usage\r\n\r\n* cleanup\r\n\r\n* no more zmq\r\n\r\n* undo that\r\n\r\n* cleanup speed limit\r\n\r\n* fix sidebar severity for athena status\r\n\r\n* not aarch64\r\n\r\nCo-authored-by: deanlee <deanlee3@gmail.com>\r\nCo-authored-by: Comma Device <device@comma.ai>\r\nCo-authored-by: Willem Melching <willem.melching@gmail.com>"
        authors= [commitinfo["author_email"]]
        try:
            if (commitinfo["msg"].find('Co-authored-by') != -1):
                for author in commitinfo["msg"].split('Co-authored-by')[1:]:
                    authors.append(author.split('<')[1].split('>')[0])
        except:
            pass
        commitMSG = commitinfo["msg"]
        keyWordAdjustment = 0
        prevCommitAdjustment = 0
        #check the commit message for the words in positiveKeyWords
        for word in positiveKeyWords:
            if (commitMSG.find(word) != -1):
                keyWordAdjustment = keyWordAdjustment + positiveKeyWordsValue
        
        #check the commit message for the words in positiveKeyWordsBigImpact
        for word in positiveKeyWordsBigImpact:
            if (commitMSG.find(word) != -1):
                keyWordAdjustment = keyWordAdjustment + positiveKeyWordsBigImpactValue

        #check the commit message for the words in negitiveKeyWords
        for word in negitiveKeyWords:
            if (commitMSG.find(word) != -1):
                keyWordAdjustment = keyWordAdjustment + negitiveKeyWordsValue

        #check the commit message for the words in prevCommitScoreAdjustmentNegitiveKeyWords
        for word in prevCommitScoreAdjustmentNegitiveKeyWords:
            if (commitMSG.find(word) != -1):
                prevCommitAdjustment = prevCommitAdjustment + prevCommitScoreAdjustmentNegitiveKeyWordsValue
        #Impliment this later
        #if (prevCommitAdjustment != 0):
            #dataSet1['grade'].last = dataSet1['grade'].last + prevCommitAdjustment

        topBaseScoreAddition = 50
        topContributorScoreAddition = 15
        topKeyWordScoreAddition = 15
        topCommitNumbScoreAddition = 20

        if (keyWordAdjustment > 5):
            KeyWordAdjustment = 5
        if (keyWordAdjustment < -5):
            KeyWordAdjustment = -5

        contributorscount = len(authors)
        if (contributorscount > 3):
            contributorscount = 3

        finalKeywordScore = (keyWordAdjustment/5)*topKeyWordScoreAddition
        finalContributorScore = ((contributorscount/3)*topContributorScoreAddition)
        finalCommitScore = (topCommitNumbScoreAddition * (i / numberOfCommits))

        if(repoBaseScore > topBaseScoreAddition):
            repoBaseScore = topBaseScoreAddition

        finalGrade = np.clip(repoBaseScore + finalKeywordScore + finalContributorScore + finalCommitScore, 0,100)
        finalPath = filesToGradeList[i][0].split(inputFolder)[1]
        df = pd.concat([df, pd.DataFrame([[finalGrade, finalPath]], columns=['fileGrade', 'Path'])])
        commitGrade.append([finalGrade, finalPath])
    return (commitGrade)
        


    

def main():
    global inputFolder, outputFolder
    args = parser.parse_args()
    inputFolder = args.input
    outputFolder = args.output
    #get time
    startTime = time.time()

    commitGrades = []
    foldersToProcess = getSubFolders(inputFolder)

    filesToProcess = getFiles(foldersToProcess)
    
    for i in range(len(foldersToProcess)):
        repositoryGrade = baseRepositoryGrading(json.loads(getGitInfo(os.path.join(inputFolder,foldersToProcess[i])).split("\n")[0]))
        repositoryFiles = filesToProcess[i]
        #print progress bar 
        print (mcall.printProgressBar(i, len(foldersToProcess), "Processing Files"))
        for j in range(len(repositoryFiles)):
            if (threads != 0):
                while (len(th.enumerate()) > threads):
                    #sleep for a second
                    time.sleep(1)
            #multithread this
            thread = th.Thread(target=commitGrades.append, args=(commitFolderGrading(getFilesToGradeFromRevisionFolder(os.path.join(inputFolder, foldersToProcess[i])+repositoryFiles[j]), repositoryGrade),))
            thread.start()
    
    length = 0
    for commits in commitGrades:
        length = length + len(commits)

    #check for output folder
    if (outputFolder != None):
        #write the output to a file in a 
        #create the output folder
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        df.to_pickle(os.path.join(outputFolder,"grades.pkl"))
        
    else :
        print (length)
        print (df)
    #get time
    endTime = time.time()
    print ("Time Taken: " + str(endTime - startTime))
main()

#Get Subfolders and return as a list




