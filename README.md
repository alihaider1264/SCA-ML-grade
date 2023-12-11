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
To get started, navigate to https://seart-ghs.si.usi.ch/ and download a JSON file of repositories for training off of. Then, use the Repo-Collector utility to download the repositories in that JSON file. For more infromation on how to do this, navigate to "/Repo-Collector/Readme.md". 
