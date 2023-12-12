## What is this? 
This is a python script that can be run either as a utility, or used as a library. This script will "score" data from the Repo-Collector part of this repository. The goal of this is to generate a general score for file revisions which while not accurate at a small scale, are relitivly accurate enough to be used for machine learning. 

## Usage
You can import Grader.py as a library or run it as it's own script. 

## Utility Usage
    -i --input  Path for the folder containing the repositories and files to be scored (required)
    -o --output Path for the folder that will get the output. 

## Library Usage
Import Grader.py, use the bootstrap method, with the input folder path as a string for the argument. This will return a dataframe.

## What is the output?
The output is a dataframe. When used with the -o flag, this dataframe will be saved to a pickle file. When used as a library, this dataframe will returned from the "bootstrap" method.

The dataframe is as follows

    Colums:
         fileGrade: The "score" of a file, represented as a floating point number
         path: The path of the file graded. Stored as a string.



