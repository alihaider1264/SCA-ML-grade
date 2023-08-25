#Get an input git log and output a new directory which contains another directory for each commit.
#Each commit directory contains a file with the full method found in the commit.
#The folder name is based on how many commits since the first (First is 0).
#There will be another file to go along it which will be a JSON file with the commit information.
#The JSON file will have the following information:
#	- commit hash
#	- author
#	- commit name
#	- commit description
#   - how many commits it's been since the first commit (again start at 0)




#impliment a size limit, some bottleneck happens when the file is too large


import argparse
from asyncio.windows_events import NULL
import os
import sys

fileSizeMax = 110000000
useFileSizeMax = True

def load_commit_log(file):
    with open(file, 'r', encoding="utf8") as f:
        try:
            return f.read()
        except:
            return NULL

def parse_commit_diff(diff):
    if (diff.startswith('-')):
        return ''
    else: 
        return str(diff[1:])

def parse_commit_log(log):
    commits = []
    current_commit = None
    incommit = False
    invalidContent = False
    for line in log.split('\n'):
        #skip the line if it has invalid characters
        if not line.isascii():
            continue
        if line.startswith('commit'):
            if current_commit != None:
                commits.append(current_commit)
                current_commit = None
                incommit = False
                invalidContent = False
            current_commit = {}
            current_commit['hash'] = line.split()[1]
            current_commit['commitcontent'] = ''
        elif incommit:
            #For some reason git log likes to duplicate itself? This is a hacky fix
            if line.startswith("@@"):
                invalidContent = True
            if not invalidContent:
                current_commit['commitcontent'] =  str(current_commit['commitcontent']) + str(parse_commit_diff(line)) + '\n'
        elif line.startswith('Author:'):
            current_commit['author'] = line.split(':')[1].strip()
        elif line.startswith('Date:'):
            current_commit['date'] = line.split(':')[1].strip()
            current_commit['summary'] = NULL
        elif line.startswith('    '):
            if current_commit['summary'] is NULL:
                current_commit['summary'] = line.strip()
                current_commit['description'] = NULL
            else:
                #description parser
                if (not line == '    '):
                    current_commit['description'] = str(current_commit['description']) + '\n' + str(line.strip())
        elif line.startswith('@@'):
            incommit = True
    commits.append(current_commit)
    return commits


def mainArgs(output,logfile):
    log = load_commit_log(logfile)
    if log == NULL:
        return
    if len(log) > fileSizeMax and useFileSizeMax:
        print('File is too large')
        return
    commits = parse_commit_log(log)
    #write commits to files
    os.makedirs(output, exist_ok=True)
    for i in range(len(commits)):
        print("test")
        with open(output + "\\" + str(i) + '.txt', 'w',encoding="utf8") as f:
            try:
                f.write(commits[i]['commitcontent'])
            except:
                print("probably unicode error")
                continue
        f.close
        commits[i].pop('commitcontent')
        with open(output + str(i) + '.json', 'w',encoding="utf8") as f:
            f.write(str(commits[i]) + '\n')
        f.close

def main():
    parser = argparse.ArgumentParser(description='Seperate a gitlog file from LogGenerator into different files with corresponding JSON files containing metadata')
    parser.add_argument('-l', '--logfile', help='The input log file', required=True)
    parser.add_argument('-o', '--output', help='The output folder', required=True)
    args = parser.parse_args()
    mainArgs(args.output,args.logfile)
#main()