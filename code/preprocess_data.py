import os
import json
from preprocessing import DataframeCreator, Preprocessor, Converter
from spacy.cli.convert import convert

# Setup
LANG="de"
DATA_VERSION="1.2"
BASEDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
WORD_FREQ_FILE_PATH=os.path.join(BASEDIR, "data/word_frequencies/de/de-100k.txt")

def _get_dataframes(split):
    data_file_path = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-{2}-de.tsv".format(LANG, DATA_VERSION, split)
    # Get data file
    data_file = open(os.path.join(BASEDIR, data_file_path), "r")
    # 1. Create dataframes
    return DataframeCreator().create_dataframes(data_file)

def preprocess_data_split(split, output_folder):
    # 1. Create dataframes
    dataframes = _get_dataframes(split)
    # 2. Preprocessing pipeline
    processed = Preprocessor().preprocess(dataframes, WORD_FREQ_FILE_PATH)
    # 3. Convert to spacy
    spacy_format = Converter().to_spacy(processed)
    # 4. Save the properly formatted output
    output_file_path = os.path.join(output_folder, '{}_doc'.format(split))
    with open(output_file_path, 'w+') as f:
        json.dump(spacy_format, f)

def preprocess_data_split_for_spacy_convert(split, output_folder):
    """
    Preprocess the raw data and save into a `spacy convert` IOB format.
    """
     # 1. Create dataframes
    dataframes = _get_dataframes(split)
    # 2. Preprocessing pipeline
    processed = Preprocessor().preprocess_for_spacy_convert(dataframes, WORD_FREQ_FILE_PATH)
    # 3. Save as .iob
    output_file_name = '{}_doc'.format(split)
    output_iob_file_path = os.path.join(output_folder, output_file_name + ".iob")
    # Remove contents
    open(output_iob_file_path, 'w').close()
    # Append each doc
    with open(output_iob_file_path, 'a+') as f:
        for dataframes, _ in processed:
            f.write("-DOCSTART- -X- O O\n")
            for sentence_df in dataframes:
                sentence_df[["TOKEN", "NE-COARSE-LIT"]].to_csv(
                    f,
                    sep="\t",
                    header=False,
                    index=False,
                )
                f.write("\n")
    convert(
        output_iob_file_path,
        output_folder,
        converter="ner",
        lang="de"
    )
    
    output_json_file_path = os.path.join(output_folder, output_file_name + ".json")
    json_file = open(output_json_file_path, 'r')
    json_data = json.load(json_file)
    for i, j_doc in enumerate(json_data):
        doc_sentences = processed[i][1]
        print(doc_sentences)
        for paragraph in j_doc.get("paragraphs"):
            paragraph["raw"] = " ".join(doc_sentences)

    outfile = open(output_json_file_path, 'w')
    json.dump(json_data, outfile)


if __name__ == "__main__":
    # Create the folder
    output_folder = os.path.join(BASEDIR, 'data/preprocessed/')
    os.makedirs(output_folder, exist_ok=True)
    # Preprocess both data splits
    preprocess_data_split_for_spacy_convert("train", output_folder)
    preprocess_data_split_for_spacy_convert("dev", output_folder)

    

    


