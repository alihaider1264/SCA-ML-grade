Since tokenization takes much longer than grading at this point, we are going to have it come before.

Input: The output folder from "Repo-Collector". This consists of a tree of files. 
Level 0 has folders for every repository downloaded. 
Level 1 should contain the folder "parsed", which is the folder of intrest for this program. It also contains the file gitinfo.txt which has information about the repository.
Level 2 inside the parsed folders contain folder which represent the branches downloaded.
Level 3 contains folders either representing methods, classes or source files of intrest.
Level 4 contains files representing each revision of code in it's whole (0.txt, 1.txt etc), along with it's metadata (0.json, 1.json).

Currently, this tokenizer is tokenizing any file ending in .txt and which isn't named "gitinfo.txt"

Output:
The output should be a panda dataframe (Subject to Change), token dictonary, and a info file.
The Dataframe should have 2 colums.
"Token Code", "Path", 

#TODO The first entry should have the date as the token code and the md5 hash of the dictonary as the path

Token Code contains the tokenized code

Path contains the relitive path of the file which the token code was generated from. 

#TODO The info file should contain any paramaters relivent to the tokenization, and a hash of the dictonary.