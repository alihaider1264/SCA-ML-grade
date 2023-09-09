#take input folder and output folder as arguments
import argparse
import SupportingClasses.CaMlSupportingClasses as mcall
import os
import pandas as pd
import datetime
import datetime

#commit comment keywords for code grade adjustment
positiveKeyWords = ['fix', 'resolve', 'resolve', 'resolved', 'resolves', 'resolving', 'close', 'closed', 'closes', 'closing', 'fixes', 'fixed', 'fixing', 'patch', 'patched', 'patching', 'update', 'updated', 'updating', 'upgrade', 'upgraded', 'upgrading', 'improve', 'improved', 'improving', 'improvement', 'improvements', 'improves', 'improving', 'enhance', 'enhanced', 'enhances', 'enhancing', 'enhancement', 'enhancements']
positiveKeyWordsBigImpact = ['Signed-off', 'Merge', 'Merged']
positiveKeyWordsValue = 1
positiveKeyWordsBigImpactValue = 5
negitiveKeyWords = ['todo','tofix','bugged','fix me','fix-me']
negitiveKeyWordsValue = -1

prevCommitScoreAdjustmentNegitiveKeyWords = ['revert','reverted','reverting','reverts']
prevCommitScoreAdjustmentNegitiveKeyWordsValue = -10


inputFolder,outputFolder = "",""
parser = argparse.ArgumentParser(description='Input a Grade Downloader folder, and this will generate grades for each file')
parser.add_argument('-i', '--input', help='The input folder', required=True)
parser.add_argument('-o', '--output', help='The output folder', required=False)
def getSubFolders(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))and name != 'git']

def getFiles(foldersToProcess):
    global inputFolder
    filesToIndex = []
    for folder in foldersToProcess:
        filesToIndex.append([mcall.searchFileName(inputFolder + folder, "0.py"), os.path.join(inputFolder, folder)])
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
    allFiles = os.listdir(FolderPath)
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
    print (filesToGradeList)

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
    
def commitFolderGrading (filesToGradeList):
    numberOfCommits = len(filesToGradeList)
    #TO:DO, PORT
    for filesToGrade in range(len(filesToGradeList)):
        print(filesToGrade)
        #get the number of contributors
        #error checking
        try:
            contributors = commitinfo.split('author\':')[1]
            contributors = contributors.split('\'date\':')[0]
            contributorscount = contributors.count("<")
        except:
            break
            print("error file = " + i+str(j)+".json")

        if (commitdata == ''):
            break
        contributorScore = contributorscount -1

        #find KeyWords in the commit message
        commitmessage = commitinfo.split('\'summary\':')[1]
        commitmessage = commitmessage.replace(', \'description\':', ' ')

        keyWordAdjustment = 0
        prevCommitAdjustment = 0
        #check the commit message for the words in positiveKeyWords
        for word in positiveKeyWords:
            if (commitmessage.find(word) != -1):
                keyWordAdjustment = keyWordAdjustment + positiveKeyWordsValue
        
        #check the commit message for the words in positiveKeyWordsBigImpact
        for word in positiveKeyWordsBigImpact:
            if (commitmessage.find(word) != -1):
                keyWordAdjustment = keyWordAdjustment + positiveKeyWordsBigImpactValue

        #check the commit message for the words in negitiveKeyWords
        for word in negitiveKeyWords:
            if (commitmessage.find(word) != -1):
                keyWordAdjustment = keyWordAdjustment + negitiveKeyWordsValue

        #check the commit message for the words in prevCommitScoreAdjustmentNegitiveKeyWords
        for word in prevCommitScoreAdjustmentNegitiveKeyWords:
            if (commitmessage.find(word) != -1):
                prevCommitAdjustment = prevCommitAdjustment + prevCommitScoreAdjustmentNegitiveKeyWordsValue
        """Impliment this later"""
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

        if (contributorscount > 3):
            contributorscount = 3

        finalKeywordScore = (keyWordAdjustment/5)*topKeyWordScoreAddition
        finalContributorScore = ((contributorScore/3)*topContributorScoreAddition)
        finalCommitScore = (topCommitNumbScoreAddition * (j / numberOfCommits))

        if(repoBaseScore > topBaseScoreAddition):
            repoBaseScore = topBaseScoreAddition


        commitGrade = np.clip(repoBaseScore + finalKeywordScore + finalContributorScore + finalCommitScore, 0,100)
        """if (commitGrade == 55):
            print(repoBaseScore)
            print(finalKeywordScore)
            print(finalContributorScore)
            print(finalCommitScore)"""
        dataSet1temp = pd.DataFrame({'data': [commitdata], 'grade': [commitGrade]})
        if (addRepoToData):
            dataSet1temp['repo'] = i.split('parsed')[0]
        dataSet1 = pd.concat([dataSet1, dataSet1temp], ignore_index=True)

        

        #calculate Grade
        #create a minimum grade based off of stats from the github repo

        #get the authors info if using the GITHUB API. Maybe make into a seperate application that can then be used to generate a json file used here due to the rate limit of the API
        if (useGITAPI == True):
            authorsArray = contributors.split('>')
            for author in authorsArray:
                if (author.find('<') != -1):
                    authorsEmail.append(author[author.find('<')+1:])
            #use https://api.github.com/search/users?q= to get a username from an email address
            for author in authorsEmail:
                print(authorsEmailCache)
                if (author.find('@') != -1 and not (author in authorsEmailCache)):
                    print (author + 'test')
                    gitRequest = requests.get('https://api.github.com/search/users?q='+author).json()
                    if (gitRequest['total_count'] > 0):
                        authors.append(gitRequest['items'][0]['login'])
                        print("shouldn't show up")

                    #print (requests.get('https://api.github.com/search/users?q='+author).json()['items'][0]['login'])



def main():
    global inputFolder, outputFolder
    args = parser.parse_args()
    inputFolder = args.input
    outputFolder = args.output

    filesToProcess = getFiles(getSubFolders(inputFolder))
    for repository in filesToProcess:
        
        for foldersToGrade in repository[0]:
            for filesToGrade in getFilesToGradeFromRevisionFolder(repository[1]+foldersToGrade):
                commitFolderGrading(filesToGrade)
                exit()
        


    
main()

#Get Subfolders and return as a list




