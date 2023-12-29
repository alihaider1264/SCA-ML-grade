# CA-ML
Repo for Code Analysis using NNs with an e2e learning philosophy.

## About this repository

This repository hosts the requirements to generate a relative code scoring model, as featured in "". This is a proof of concept model to show that pre labeled datasets or LLMs are not necessarily required to have a universal neural network for ranking code. 

## Why is this a thing
While reviewing automated code scoring, we noticed a trend. Often times, neural networks made for code scoring are specifically made for one problem, and often requires a vast amount of hand labeled data. We wanted to try and create a solution which does not require the labeling, and can be used across a wide variety of code.

## "You should just use a LLM"
While LLMs are amazing, and provide many benefits over our approach, we believe that there is value to looking into alternatives. High quality LLMs fit for this task are often not able to run locally, and consume a vast amount of power. 

## Directory Structure
    .
    ├── Auto-Grader               # Automatic labler that scores based on metadata and assumptions
    ├── DummyData                 # Dummy testing data for python
    └── Model Generation          # Everything used to generate the model and test it
        ├── SCA-Tokenizer         # Tokenizer/Vectorizer used with language specific modifications
    ├── Repo-Collector            # Script and Libraries to download repositories used for training and testing

## Get Started Generating Your Own Model
To get started, navigate to https://seart-ghs.si.usi.ch/ and download a JSON file of repositories for training off of. Then, use the Repo-Collector utility to download the repositories in that JSON file. For more infromation on how to do this, navigate to "/Repo-Collector/Readme.md". Then, run the genModelPrereqs.sh file with your Repo Downloads folder as the first argument, and an output folder as your second argument. Preforming this will have you ready to go to the Model Generation readme, and follow the instructions there.

## Commit Structure
As we make changes to this repository, we are continuing developing and testing new models and addessing their pperformance. To help maintain clairty, we attempt to adhear to the following structure. Commits which include the word "Model" usually signify that a commit contains both a model creation notebook and corresponding model testing, synchronized with each other. This means the model creation notebook remains unchanged from when we generated the model being evaluated in the testing notebooks. This should allow a easy way to keep track of what changes are causing improvements and regressions.
