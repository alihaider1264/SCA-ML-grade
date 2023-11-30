#!/bin/bash

#genModelPrereqs.sh ~/SPDataset/smallDataset/S2DS245-1014/ ~/SPGenerations/
#genModelPrereqs.sh ~/SPDataset/smallDataset/S2DS245-1014/ /mnt/SPDrive/SPGenerations
#genModelPrereqs.sh /mnt/SPDrive/MiniDatasetPath/CPPTest1/ /mnt/SPDrive/SPGenerationsCPP
#./genModelPrereqs.sh /home/jaredrussell/CPPDataset/ /home/jaredrussell/CPPMLGen/


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

catigory_input=$token_path
catigory_path=$token_path





#Run this file using the following command:
python3 ./Auto-Grader/Grader.py -i $dataset_path -o $grades_path 
#Run this file using the following command:
python3 ./Model-Generation/SCA-Tokenizer/TokenizerManager.py -i $dataset_path -o $token_path
#Run this file using the following command:
#python3 ./Model-Generation/TokenCatigoryGenerator/TokenCatigoryGenerator.py -i $token_path -o $token_path
#Run this file using the following command:
#python3 ./Model-Generation/TokenCatigoryGenerator/TokenCatigoryApplier.py -i $token_path -o $token_path



