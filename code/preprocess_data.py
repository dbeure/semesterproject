from preprocessing import DataframeCreator, Preprocessor, Converter

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)

if __name__ == "__main__":
    # Get data file
    data_file = open(DATA_FILE_PATH, "r")
    # 1. Create dataframes
    dataframes = DataframeCreator().create_dataframes(data_file)
    # 2. Preprocessing pipeline
    processed = Preprocessor().preprocess(dataframes[:1])
    # 3. Convert to spacy
    spacy_format = Converter().to_spacy(processed)
    

    


