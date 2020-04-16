from dataframe_creator import DataframeCreator
from preprocessor import Preprocessor

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)


if __name__ == "__main__":
    # Get data file
    data_file = open(DATA_FILE_PATH, "r")
    # Create dataframes
    dataframes = DataframeCreator().create_dataframes(data_file)
    # Preprocessing pipeline
    Preprocessor().preprocess(dataframes)
    


    


