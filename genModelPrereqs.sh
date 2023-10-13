#!/bin/bash

# Store input paths as variables
#!/bin/bash
# Display command output
set -x

dataset_path=$1
output_path=$2
datevar=$(date +%s)


grades_path=$output_path"Grades/"
grades_path=$grades_path$datevar

token_path=$output_path"Tokens/"
token_path=$token_path$datevar




#Run this file using the following command:
python3 ./Auto-Grader/Grader.py -i $dataset_path -o $grades_path 
#Run this file using the following command:
python3 ./Model-Generation/SCA-Tokenizer/TokenizerManager.py -i $dataset_path -o $token_path


