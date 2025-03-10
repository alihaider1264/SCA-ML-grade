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
negitiveKeywordImpact = 0



threads = 16

prevCommitScoreAdjustmentNegitiveKeyWords = ['revert','reverted','reverting','reverts', 'undo', 'undid', 'undone', 'undoing']
prevCommitScoreAdjustmentNegitiveKeyWordsValue = -15
df = pd.DataFrame(columns=['fileGrade', 'Path'])

#Stats about what the grader is doing
collectStats = True
deletedFiles = 0
rejectedFiles = []
ageScoresUsed = 0
contributorScoresUsed = 0
starScoresUsed = 0
forkScoresUsed = 0
watchScoresUsed = 0
issuesScoresUsed = 0
posKeyWordScoresUsed = 0
posKeyWordScoresFilesAffected = 0
posKeyWordsBigImpatUsed = 0
posKeyWordBigImpactFilesAffected = 0
specificHashDowngraded = 0

negKeyWordScoresUsed = 0

prevCommitScoresUsed = 0
commitScoresUsed = 0


inputFolder,outputFolder = "",""
parser = argparse.ArgumentParser(description='Input a Grade Downloader folder, and this will generate grades for each file')
parser.add_argument('-i', '--input', help='The input folder', required=True)
parser.add_argument('-o', '--output', help='The output folder', required=False)
def getSubFolders(path):
    return([name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) and name != "git"])

def getFiles(foldersToProcess,path):
    global inputFolder
    inputFolder = path
    filesToIndex = []
    for folder in foldersToProcess:
        filesToIndex.append(mcall.searchFileName(os.path.join(path,folder), "0.py"))
    return filesToIndex

def getGitInfo(gitInfoPath):
    with open(os.path.join(gitInfoPath,"git.info"), 'r', encoding="utf8") as file:
        data = file.read()
        return data

#This expects a folder full of .py files and .json files with files names corisponding to numbers such as 0,1,2
#If there's missing files we expect them to be because of duplicates or the file getting deleted at some point
def getFilesToGradeFromRevisionFolder(FolderPath, codeExtension=".py", jsonExtension=".json"):
    # check to see if it's a dir or a file, if it's a file strip it
    if os.path.isfile(FolderPath):
        FolderPath = FolderPath.split("0.py")[0]
    # List the files in a directory
    filesToGradeList = []
    deletedFile = False
    try:
        with os.scandir(FolderPath) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(codeExtension):
                    json_file = os.path.join(FolderPath, entry.name.replace(codeExtension, jsonExtension))
                    if os.path.exists(json_file):
                        filesToGradeList.append([entry.path, json_file])
                    else:
                        if entry.name == "DELETED.py":
                            deletedFile = True
            # sort the files in numerical order
            filesToGradeList.sort(key=lambda x: int(os.path.basename(x[0]).split(".")[0]))
    except:
        return filesToGradeList
    fileCount = len(filesToGradeList)
    # check to see if it's odd
    if deletedFile:
        filesToGradeList.append(["DELETED", "DELETED"])
    return filesToGradeList

def baseRepositoryGrading(repoInfo):

    global negitiveKeywordImpact
    global deletedFiles
    global rejectedFiles
    global ageScoresUsed
    global contributorScoresUsed
    global starScoresUsed
    global forkScoresUsed
    global watchScoresUsed
    global issuesScoresUsed
    global posKeyWordScoresUsed
    global posKeyWordScoresFilesAffected
    global posKeyWordsBigImpatUsed
    global posKeyWordBigImpactFilesAffected
    global negKeyWordScoresUsed
    global prevCommitScoresUsed
    global commitScoresUsed
    
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
    if collectStats:
        global ageScoresUsed
        global contributorScoresUsed
        global starScoresUsed
        global forkScoresUsed
        global watchScoresUsed
        global issuesScoresUsed
        if ageScore in top2Scores:
            ageScoresUsed = ageScoresUsed + 1
        if contributorRepoScore in top2Scores:
            contributorScoresUsed = contributorScoresUsed + 1
        if starScore in top2Scores:
            starScoresUsed = starScoresUsed + 1
        if forkScore in top2Scores:
            forkScoresUsed = forkScoresUsed + 1
        if watchScore in top2Scores:
            watchScoresUsed = watchScoresUsed + 1
        if issuesScore in top2Scores:
            issuesScoresUsed = issuesScoresUsed + 1
    #add the top 2 scores together
    repoBaseScore = repoBaseScore + top2Scores[0] + top2Scores[1]
    repoBaseScore = repoBaseScore/50
    if (issuesScore == -1):
        repoBaseScore = repoBaseScore -15
    return repoBaseScore
    
def commitFolderGrading(filesToGradeList, repoBaseScore, commitsLowerLimit = 5):
    global df
    global negitiveKeywordImpact
    global deletedFiles
    global rejectedFiles
    global ageScoresUsed
    global contributorScoresUsed
    global starScoresUsed
    global forkScoresUsed
    global watchScoresUsed
    global issuesScoresUsed
    global posKeyWordScoresUsed
    global posKeyWordScoresFilesAffected
    global posKeyWordsBigImpatUsed
    global posKeyWordBigImpactFilesAffected
    global negKeyWordScoresUsed
    global prevCommitScoresUsed
    global commitScoresUsed
    global specificHashDowngraded
    #

    #filesToGradeList is formatted as [code path, json path]
    numberOfCommits = len(filesToGradeList)
    commitGrade = []
    for i in range(numberOfCommits):
        if numberOfCommits < commitsLowerLimit:
            return commitGrade
        # get files
        commitinfo = ''
        currentJSONFilePath = filesToGradeList[i][1]
        if currentJSONFilePath == "DELETED":
            #deduct 50% of score for the whole file
            for commitGradeIndex in range(len(commitGrade)):
                commitGrade[commitGradeIndex][0] = commitGrade[commitGradeIndex][0] * .5
                deletedFiles = deletedFiles + 1
            continue
        try:
            with open(currentJSONFilePath, 'r', encoding="utf8") as file:
                commitinfo = json.loads(file.read())
        except Exception as e:
            print(f"Error opening {currentJSONFilePath}: {e}")
            continue
        commitHash = commitinfo.get("hash")

        # get the number of contributors
        # Formatting = "msg": "UI vision refactor (#2115)\n\n* refactor vision\r\n\r\n* don't show slow frame message when in preview mode\r\n\r\n* change draws to uint32_t\r\n\r\n* set vision_seen=false after destroy\r\n\r\n* remove vision_connect_thread\r\n\r\n* refactor ui_update\r\n\r\n* seelp 30ms when vision is not connected\r\n\r\n* remove should_swap\r\n\r\n* call ui_update_sizes before ui_draw\r\n\r\n* rebase\r\n\r\n* start bigger UI refactor\r\n\r\n* don't need the touch fd\r\n\r\n* fix qt build\r\n\r\n* more cleanup\r\n\r\n* more responsive\r\n\r\n* more refactor\r\n\r\n* fix for pc\r\n\r\n* poll for frames\r\n\r\n* lower CPU usage\r\n\r\n* cleanup\r\n\r\n* no more zmq\r\n\r\n* undo that\r\n\r\n* cleanup speed limit\r\n\r\n* fix sidebar severity for athena status\r\n\r\n* not aarch64\r\n\r\nCo-authored-by: deanlee <deanlee3@gmail.com>\r\nCo-authored-by: Comma Device <device@comma.ai>\r\nCo-authored-by: Willem Melching <willem.melching@gmail.com>"
        try:
            authors = [commitinfo.get("author_email")] + [author.split("<")[1].split(">")[0] for author in commitinfo.get("msg", "").split("Co-authored-by")[1:]]
        except:
            authors = [commitinfo.get("author_email")]
        commitMSG = commitinfo.get("msg", "")

        keyWordAdjustment = 0
        prevCommitAdjustment = 0

        # check the commit message for the words in positiveKeyWords
        for word in positiveKeyWords:
            if word in commitMSG:
                keyWordAdjustment += positiveKeyWordsValue
                #Stats
                posKeyWordScoresUsed = posKeyWordScoresUsed + 1
                if keyWordAdjustment == positiveKeyWordsValue:
                    posKeyWordScoresFilesAffected = posKeyWordScoresFilesAffected + 1

        # check the commit message for the words in positiveKeyWordsBigImpact
        for word in positiveKeyWordsBigImpact:
            if word in commitMSG:
                keyWordAdjustment += positiveKeyWordsBigImpactValue
                #Stats
                posKeyWordsBigImpatUsed = posKeyWordsBigImpatUsed + 1
                if keyWordAdjustment == positiveKeyWordsBigImpactValue:
                    posKeyWordBigImpactFilesAffected = posKeyWordBigImpactFilesAffected + 1


        # check the commit message for the words in negitiveKeyWords
        for word in negitiveKeyWords:
            if word in commitMSG:
                keyWordAdjustment += negitiveKeyWordsValue
                #Stats
                negKeyWordScoresUsed = negKeyWordScoresUsed + 1


        # check the commit message for the words in prevCommitScoreAdjustmentNegitiveKeyWords
        for word in prevCommitScoreAdjustmentNegitiveKeyWords:
            if word in commitMSG:
                prevCommitAdjustment = prevCommitAdjustment + prevCommitScoreAdjustmentNegitiveKeyWordsValue
                #Stats
                prevCommitScoresUsed = prevCommitScoresUsed + 1

        if (prevCommitAdjustment != 0):
            useFallback = True
            deleteBadCommit = False
            #Check for "This reverts commit" message
            if "This reverts commit" in commitMSG:
                commitBeingReverted = commitMSG.split("This reverts commit ")[1].split(".")[0]
                #strip anything after the hash
                if len(commitBeingReverted) > 40:
                    commitBeingReverted = commitBeingReverted[:40]
                #find the commit being reverted
                for commitGradeIndex in range(len(commitGrade)):
                    if commitGrade[commitGradeIndex][2] == commitBeingReverted:
                        if deleteBadCommit:
                            #delete the bad commit
                            commitGrade.pop(commitGradeIndex)
                        else:
                            commitGrade[commitGradeIndex][0] = commitGrade[commitGradeIndex][0] + (prevCommitAdjustment*1.5)
                        specificHashDowngraded = specificHashDowngraded + 1
                        useFallback = False
                        break
            if useFallback:
                
                #add prevCommitAdjustment to the previous commit
                prevCommitsToAdjust = 1
                if (i > prevCommitsToAdjust - 1):
                    for j in range(prevCommitsToAdjust):
                        if deleteBadCommit:
                            #delete the bad commit
                            try:
                                commitGrade.pop(i - j - 1)
                            except: 
                                pass
                        else:
                            commitGrade[i - j - 1][0] = commitGrade[i - j - 1][0] + prevCommitAdjustment

                #stats
                prevCommitScoresUsed = prevCommitScoresUsed + 1
            

        topBaseScoreAddition = 50
        topContributorScoreAddition = 15
        topKeyWordScoreAddition = 15
        topCommitNumbScoreAddition = 20

        if keyWordAdjustment > 5:
            keyWordAdjustment = 5
        elif keyWordAdjustment < -5:
            keyWordAdjustment = -5

        contributorscount = len(authors)
        if contributorscount > 3:
            contributorscount = 3

        finalKeywordScore = (keyWordAdjustment / 5) * topKeyWordScoreAddition
        finalContributorScore = ((contributorscount / 3) * topContributorScoreAddition)
        finalCommitScore = (topCommitNumbScoreAddition * (i / numberOfCommits))

        repoBaseScore = min(repoBaseScore, topBaseScoreAddition)

        finalGrade = np.clip(repoBaseScore + finalKeywordScore + finalContributorScore + finalCommitScore, 0, 100)
        if finalGrade < 0:
            finalGrade = 0
        finalPath = filesToGradeList[i][0].split(inputFolder)[1]
        commitGrade.append([finalGrade, finalPath, commitHash])
    #clear any empty rows
    commitGrade = [x for x in commitGrade if x != []]
    #hide futurewarning
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    #make commitGrade only have the first 2 columns
    commitGradeToAppend = []
    for commit in commitGrade:
        commitGradeToAppend.append(commit[:2])
    if (len(commitGradeToAppend) > 0):
        df = pd.concat([df, pd.DataFrame(commitGradeToAppend, columns=['fileGrade', 'Path'])], ignore_index=True)
    
    return (commitGrade)
        


    

def main():
    global inputFolder, outputFolder
    args = parser.parse_args()
    inputFolder = args.input
    outputFolder = args.output
    bootstrap(inputFolder, outputFolder)
    
def bootstrap(inputFolder, outputFolder = None, dateAsFileName = False):
    #start time
    startTime = time.time()

    commitGrades = []
    foldersToProcess = getSubFolders(inputFolder)

    filesToProcess = getFiles(foldersToProcess, inputFolder)
    
    for i in range(len(foldersToProcess)):
        repositoryGrade = baseRepositoryGrading(json.loads(getGitInfo(os.path.join(inputFolder,foldersToProcess[i])).split("\n")[0]))
        repositoryFiles = filesToProcess[i]
        #print progress bar 
        mcall.printProgressBar(i, len(foldersToProcess), prefix = "Processing Files", suffix = "Complete", length = 50)
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
        print ("Specific Hashes Downgraded: " + str(specificHashDowngraded))
        print("Other downgrades: " + str(prevCommitScoresUsed))
        
    #end time
    endTime = time.time()
    print ("Time Taken: " + str(endTime - startTime))
    return df

if __name__ == "__main__":
    main()

#Get Subfolders and return as a list




