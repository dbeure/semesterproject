import pandas as pd
import re

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)

if __name__ == "__main__":
    # Get data file
    data_file = open(DATA_FILE_PATH, "r")

    # Create the corpus dataframe
    corpus_df = pd.read_csv(
        data_file,
        sep='\t',
        skip_blank_lines=True,
        comment="#",
        quoting=3
    )

    print(corpus_df.info())