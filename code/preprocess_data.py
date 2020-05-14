import os
from preprocessing import DataframeCreator, Preprocessor, Converter

# Setup
LANG="de"
DATA_VERSION="1.1"
BASEDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
DATA_FILE_PATH="data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)
WORD_FREQ_FILE_PATH=os.path.join(BASEDIR, "data/de-100k.txt")

if __name__ == "__main__":
    # Get data file
    data_file = open(os.path.join(BASEDIR, DATA_FILE_PATH), "r")
    # 1. Create dataframes
    dataframes = DataframeCreator().create_dataframes(data_file)
    # 2. Preprocessing pipeline
    processed = Preprocessor().preprocess(dataframes[:1], WORD_FREQ_FILE_PATH)
    # 3. Convert to spacy
    spacy_format = Converter().convert_all_docs_to_spacy(processed)
    spacy_format = spacy_format[0]
    print(spacy_format)
    # 4. Save the properly formatted output
    # Create the folder
    output_folder = os.path.join(BASEDIR, 'data/preprocessed/')
    os.makedirs(output_folder, exist_ok=True)
    for i, d in enumerate(spacy_format):
        output_file_path = os.path.join(output_folder, 'train_doc_{}'.format(i))
        f = open(output_file_path, 'w+')
        f.write(str(d))
    

    

    


