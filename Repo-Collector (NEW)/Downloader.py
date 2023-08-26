import SupportingClasses.CaMlSupportingClasses as mcall
import argparse
import os
import json
from pydriller import Repository
import time
import subprocess
import threading
import queue
import atexit


#A new repository collector which uses pydriller
#MISSING FEATURES: 
    #Method Seperation/Class Seperation (Probably should be done outside of the downloader. Maybe make a parser for this?)
    #Multithreading will add later

#NEW FEATURES
    #Easier to manage
    #Cross platform

isBatchJson = False
repoLocation = []
outputLocation = ""
branch = ""
submodules = False
multibranch = False
defJSON = ""
language = ""
noDupe = False
hashMemory = []
keepGit = False
maxThreads = 20



def processRepo(repo, repoInfo : json):
    global isBatchJson, outputLocation, branch, submodules, multibranch, defJSON, language, noDupe, repoLocation

    #start timer
    startTime = time.time()
    """Folder Structure:
    (RepoName)
        RepoInfo.JSON
        (FileName)
            0.py (Commit Data)
            0.json (Commit Info)
            1.py
            1.json
            ...
            """
    basePath = ''
    repoName = ''
    #create output folder
    gitOutputFolder = os.path.join(outputLocation, "git", str(repoInfo['id']))
    if (not os.path.exists(os.path.join(outputLocation, "git"))):
        os.mkdir(os.path.join(outputLocation, "git"))
    if (not os.path.exists(gitOutputFolder)):
        #create base folder
        os.mkdir(gitOutputFolder)
    else:
        #delete old files
        process1 = subprocess.run("rmdir "+ gitOutputFolder + " /s /q", shell=True)
    if repoName == "":
        repoName = str(repoInfo['id'])
        #create base folder
        basePath = os.path.join(outputLocation, repoName)
        if (not os.path.exists(basePath)):
            os.mkdir(basePath)
        else:
            #check for finished file
            if (os.path.exists(os.path.join(basePath, "git.info"))):
                return
            else:
                #delete old files
                for root, dirs, files in os.walk(basePath):
                    for file in files:
                        os.remove(os.path.join(root, file))     
    repoClass = Repository(repo , only_modifications_with_file_types=['.py'],clone_repo_to = gitOutputFolder)
    for commit in repoClass.traverse_commits():
        for file in commit.modified_files:
            if (file.filename.endswith(".py") and file.filename.split(".")[0] != ''):
                fileNameNoExt = file.filename.split(".")[0]
                if file.source_code is not None:

                    #TODO check file.newpath and include path in foldername
                    filePath = os.path.join(basePath,file.new_path)
                    #generate all folders in path
                    if (not os.path.exists(filePath)):
                        os.makedirs(filePath)
                    
                    exsistingFiles = os.listdir(filePath)
                    count = str((len(exsistingFiles)/2)).split(".")[0]
                    
                    #write commit data
                    skip = False
                    #Rewrite this eventually. 
                    if (noDupe):
                        #check for duplicates
                        if (len(hashMemory) > 0):
                            for i in range(len(hashMemory)):
                                if (hashMemory[i][0] == commit.hash):
                                    if (repoInfo['isFork']):
                                        #if it's a fork stop the commit from being added
                                        skip = True
                                    else :
                                        #delete the other commit
                                        os.remove(hashMemory[i][1])
                                        #delete the other commit info
                                        os.remove(hashMemory[i][1].split(".")[0] + ".json")
                                        #write 2 dummy file
                                        commitData = open(hashMemory[i][1].split(".")[0]+ "DUPLICATE" + ".txt", "w", encoding="utf8")
                                        commitData.write("DUPLICATE")
                                        commitData.close()
                                        commitData = open(hashMemory[i][1].split(".")[0] +"DUPLICATE" +".jsn", "w")
                                        commitData.write("DUPLICATE")
                                        commitData.close()
                                        
                                        #remove from memory
                                        hashMemory.pop(i)
                                        break
                    if (skip):
                        #write 2 dummy file
                        commitData = open(os.path.join(filePath, count+ "DUPLICATE" + ".txt"), "w", encoding="utf8")
                        commitData.write("DUPLICATE")
                        commitData.close()
                        commitData = open(os.path.join(filePath,count+ "DUPLICATE" + ".jsn"), "w")
                        commitData.write("DUPLICATE")
                        commitData.close()
                        
                        continue
                    #generate hash
                    hash = [commit.hash, os.path.join(repoName, file.new_path, count + ".py")]            
                    hashMemory.append(hash)
                    
                    
                    commitData = open(os.path.join(filePath, count + ".py"), "w", encoding="utf8")
                    commitData.write(str(file.source_code))
                    commitData.close()
                    #write commit info
                    commitInfo = open(os.path.join(filePath, count + ".json"), "w")
                    commitInfoJSON = {}
                    commitInfoJSON['hash'] = str(commit.hash)
                    commitInfoJSON['author'] = str(commit.author.name)
                    commitInfoJSON['author_email'] = str(commit.author.email)
                    commitInfoJSON['author_date'] = str(commit.author_date)
                    commitInfoJSON['committer'] = str(commit.committer.name)
                    commitInfoJSON['committer_email'] = str(commit.committer.email)
                    commitInfoJSON['committer_date'] = str(commit.committer_date)
                    commitInfoJSON['msg'] = str(commit.msg)
                    commitInfoJSON['merge'] = str(commit.merge)
                    commitInfoJSON['parents'] = str(commit.parents)
                    commitInfoJSON['author_timezone'] = str(commit.author_timezone)
                    commitInfoJSON['committer_timezone'] = str(commit.committer_timezone)
                    commitInfoJSON['branches'] = str(commit.branches)
                    commitInfoJSON['in_main_branch'] = str(commit.in_main_branch)
                    
                    

                    commitInfo.write(json.dumps(commitInfoJSON))
                    #TODO: Add commit info
                    commitInfo.close()
                elif (os.path.exists(filePath)): 
                    commitData = open(os.path.join(filePath, "DELETED" + ".NA"), "w", encoding="utf8")
                    commitData.write("DELETED")
                    commitData.close()
    #delete git folder fix later (Right now will only work on windows)
                
    process1 = subprocess.run("rmdir "+ gitOutputFolder + " /s /q", shell=True)

    #end timer
    endTime = time.time()
    #write the git.info file and add time to it 
    gitInfo = open(os.path.join(basePath, "git.info"), "w")
    gitInfo.write(json.dumps(repoInfo))
    gitInfo.write("\n")
    gitInfo.write("Time to generate: " + str(endTime - startTime))
    gitInfo.close()


def exit_handler():
    
    global outputLocation, hashMemory
    hashFile = open(os.path.join(outputLocation, "hashes.txt"), "a")
    hashFile.write(json.dumps(hashMemory))
    hashFile.close()



def main():
    atexit.register(exit_handler)
    parser = argparse.ArgumentParser(description='The thing that makes LogGen and GitDownloader work together')
    parser.add_argument('-r', '--repo', help='The Repo to generate diffs for (Assumes internet repos or batch json file from SEART)', required=True)
    parser.add_argument('-o', '--output', help='The output folder', required=True)
    parser.add_argument('-b', '--branch', help='Specify the branch, write all for every branch', required=False)
    parser.add_argument('-s', '--submodules', help='Download submodules', default=False, action="store_true")
    parser.add_argument('-m', '--multithread', help='Enter the amount of threads, default is 20', required=False, default=20, type=int)
    parser.add_argument('-d', '--defJSON', help='the definitions of the file formats', required=False)
    parser.add_argument('-l', '--language', help='the language to generate logs with', required=False)
    parser.add_argument('-se', '--seart', help='use a seart JSON file defined with --repo',  default=False, action="store_true")
    parser.add_argument('-nd', '--keepGit', help='Keep the Git files for later use', default=False, action="store_true")




    args = parser.parse_args()

    global isBatchJson, outputLocation, branch, submodules, multibranch, defJSON, language, noDupe, repoLocation, keepGit, maxThreads, hashMemory

    isBatchJson = args.repo.endswith(".json")
    outputLocation = args.output
    branch = args.branch
    submodules = args.submodules
    defJSON = args.defJSON
    language = args.language
    keepGit = args.keepGit
    maxThreads = args.multithread
    repoLocation = []
    #check for hash file
    try:
        if (os.path.exists(os.path.join(outputLocation, "hashes.txt"))):
            hashFile = open(os.path.join(outputLocation, "hashes.txt"), "r")
            hashMemory = json.load(hashFile)
            hashFile.close()
    except:
        print ("Hash file is corrupted, deleting")
        os.remove(os.path.join(outputLocation, "hashes.txt"))
    if (isBatchJson):
        #check for file specified
        if (os.path.exists(args.repo)):
            with open(args.repo, encoding="utf8") as f:
                data = json.load(f)
                for i in data['items']:
                    #generate base folder for repo
                    gitname = i['name']
                    gitrepo = "https://github.com/" + gitname + ".git"
                    repoLocation.append([gitrepo, i])
                    
    repoCounter = 0 
    for repo in repoLocation:
        repoCounter += 1
        mcall.printProgressBar(repoCounter, len(repoLocation), prefix = 'Progress:', suffix = 'Complete', length = 50)
        
        t = threading.Thread (target=processRepo, args=(repo[0], repo[1]))
        while (threading.active_count() > maxThreads):
            time.sleep(1)
        t.start()
    print ("Finishing last entries")
    while (threading.active_count() > 1):
        time.sleep(1)
        
main()


