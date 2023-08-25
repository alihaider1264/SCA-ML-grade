import argparse
import json
import subprocess



#downloads a repo


def downloadRepo(repo, path, branch , BranchReturn , submodules):
    if branch is not None:
        branchtext = ' -b ' + branch + ' '
        branchpath = path + '\\' + branch
    else:
        branchtext = ''
        branchpath = path + "\main"
    print("git clone "+ branchtext + repo + " "+ branchpath)
    process1 = subprocess.run("git clone "+ branchtext + repo + " "+ branchpath, shell=True)
    if (submodules):
        process2 = subprocess.run("cd /d " + branchpath + "&& git submodule update --init --recursive", shell=True)
    if (BranchReturn):
        processForBranches = subprocess.run("git -C "+ branchpath + " branch -r  ", stdout=subprocess.PIPE)
        Branches = processForBranches.stdout.decode('utf-8').split('\n')
        branchlist = []
        for branch in Branches:
            if branch != "":
                branch = branch.split("/")[1]
                branchlist.append(branch)

        print (branchlist)
        return branchlist
    return None

def main():
    parser = argparse.ArgumentParser(description='Downloads a Repo')
    parser.add_argument('-r', '--repo', help='The Repo to Download', required=True)
    parser.add_argument('-o', '--output', help='The output folder', required=True)
    parser.add_argument('-b', '--branch', help='The branch to download', required=False)
    #parser.add_argument('-mb', '--multipleBranches', help='Prints all branches', default=False, action="store_true")
    parser.add_argument('-s', '--submodules', help='Download submodules', default=True, action="store_false")
    #parser.add_argument('-usc', '-unsquash', help='Attempts to unsquash commits', default=False, action="store_true") #IS THIS POSSIBLE? PROBABLY NOT!


    args = parser.parse_args()
    downloadRepo(args.repo, args.output, args.branch, False, args.submodules)

#main()