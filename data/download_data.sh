#!/bin/bash

DATA_FOLDER=./raw

# Create data folder
mkdir $DATA_FOLDER

# If it already exists, remove it
test $? -eq 0 || rm -rf $DATA_FOLDER

# Clone the repo / re-download
git clone --depth=1 --branch=master https://github.com/impresso/CLEF-HIPE-2020.git $DATA_FOLDER

# Remove the .git folder
mv $DATA_FOLDER/data .
rm -rf $DATA_FOLDER
mv data $DATA_FOLDER