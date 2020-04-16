from dataframe_creator import DataframeCreator
from preprocessor import Preprocessor
from spacy_converter import Converter

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)

def save_datafram_to_tsv(dataframe, filename="dataframe.tsv"):
    processed_df_file = open(filename, 'w')
    processed_df_file.write(dataframe.to_csv(sep='\t', index=False))


if __name__ == "__main__":
    # Get data file
    data_file = open(DATA_FILE_PATH, "r")
    # Create dataframes
    dataframes = DataframeCreator().create_dataframes(data_file)
    # Preprocessing pipeline
    Preprocessor().preprocess(dataframes[:2])

    #print(dataframes[:1])
    print(Converter().text_from_dataframe_tokens(dataframes[0]))
    

    


