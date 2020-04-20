from preprocessing import DataframeCreator, Preprocessor, Converter, df_to_json_format

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)

def save_dataframe_to_tsv(dataframe, filename="dataframe.tsv"):
    processed_df_file = open(filename, 'w')
    df_with_selected_cols = dataframe[['TOKEN', 'NE-COARSE-LIT', 'NE-COARSE-LIT', 'NE-FINE-LIT']]
    df_csv = df_with_selected_cols.to_csv(sep='\t', index=False)
    processed_df_file.write(df_csv)


if __name__ == "__main__":
    # Get data file
    data_file = open(DATA_FILE_PATH, "r")
    # Create dataframes
    dataframes = DataframeCreator().create_dataframes(data_file)
    # Preprocessing pipeline
    Preprocessor().preprocess(dataframes[:2])

    #print(dataframes[:1])
    save_dataframe_to_tsv(dataframes[0])
    df_to_json_format(dataframes[0], "dataframe_manual.json", "UNK")
    print(Converter().text_from_dataframe_tokens(dataframes[0]))
    

    


