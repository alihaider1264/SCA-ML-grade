## What is this
This is a utility to download a collection of repositories using a SEART Github Search Engine generated JSON file. 


## Usage
This program can be used as a utility.

## Utility Arguments
-r --repo         File path for the SEART JSON file (Required)

-o --output       Output path (Required)

-m --multithread  Amount of threads to use (Default = 20)

## Internal Flags
Windows:           Set true if using windows, false for unix systems

CLEANUPOLDEDIT:    Set true if you want to clean up any left over files. This will do that and then exit the program

filesTypes:        The array of file formats to get revisisions from.

repolimit:         Max numbers of repos to download


