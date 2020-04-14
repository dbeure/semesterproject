import pandas as pd
import re

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)

def get_raw_data(path):
    """Read the original data into a string"""
    return open(path, "r").read()

def split_into_documents(corpus):
    """Split a corpus into multiple documents by a regex"""
    empty_line_pattern = re.compile("\n\n")
    return empty_line_pattern.split(corpus)

def split_first_line(corpus):
    return corpus.split("\n", 1)

def remove_document_metadata(document):
    return 

if __name__ == "__main__":
    # Get raw data string from the supplied data file
    raw_data = get_raw_data(DATA_FILE_PATH)
    # Save the first line containing metadata for later
    corpus_metadata, raw_corpus = split_first_line(raw_data)
    # Split the corpus into documents
    documents = split_into_documents(raw_corpus)
    
    print(corpus_metadata)
    print(len(documents))