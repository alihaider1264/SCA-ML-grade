## What is this
This is where the machine learning model creation and training happens, along with testing. It is also where SCA-Tokenizer lives. For more information about SCA-Tokenizer, please visit it's Readme. 

## Minimum Requirements.
We have been doing our model training on a 15GB GPU. 

## Model Creation Usage
To generate a model, you much generate the genModelPrereqs.sh file at the root of this repository. Once that is done, you can use the Model Creation notebook. At the top of the notebook, there are some variables that need to be set. At minimum, combinedInputPath and modelOutputPath need to be set. Please read the comments on the notebook to see what else can be set. Once set, all of the cells in the notebook can be ran. It will generate a output in the model output folder with a name based off of the timestamp of creation. 

## Model Testing Usage
To test a model, you need to use the Model Testing Notebook. The first cell contains code to load previous testing results. The second cell contains variables you can set. At a minimum, pathToModelFolder and pathToDataFolder need to be set. For applicable results, please ensure that you have only new data in the testing data folder. By default, this will use the latest model created. This will preform tests by comparing older commits to newer commits. Most importantly, it has a "Gap" test at the bottom which is how we mostly mesure the models performance. 

## Geeks4Geeks Testing Usage
To see how a model preforms on unmodified, randomly collected public data, we have devised tests which use Geeks4Geeks practice problems, and their submissions. To collect this data, please refer to https://github.com/mcallbosco/g4gPPS . 
