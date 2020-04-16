import json
import logging
import sys
from dataframe_creator import DataframeCreator

# Setup
LANG="de"
DATA_VERSION="1.1"
DATA_FILE_PATH = "data/raw/training-v{1}/{0}/HIPE-data-v{1}-train-de.tsv".format(LANG, DATA_VERSION)


def df_to_json_format(df, output_path, unknown_label):
    try:
        fp = open(output_path, 'w')  # output file
        data_dict = {}
        annotations = []
        label_dict = {}
        s = ''  # will be the content
        start = 0   # index of tokens
        for index, row in df.head(500).iterrows():  # only first 200 lines for now
            # if not row['TOKEN'].startswith('# document_id ='):  # change "sentence" if the document is new!
            if not row['TOKEN'].startswith('.'):
                word = row['TOKEN'] # token
                entity = row['NE-COARSE-LIT']   # label
                s += word + " " # sentence + word + empty space
                if entity != unknown_label: # what is this even for?
                    if entity != 'O':    # originally : len(entity) != 1, but here: if the label is a NER
                        d = {'text': word, 'start': start, 'end': start + len(
                            word) - 1}  # dictionary contains information about the point: word, start and end
                        # add the words to the label, results in this format:
                        # {'GEO': [{'text': 'London', 'start': 10, 'stop': 15}]}
                        try:    # if label already had words attached
                            label_dict[entity].append(d)
                        except: # if first word of that label
                            label_dict[entity] = []
                            label_dict[entity].append(d)
                start += len(word) + 1  # the start index is updated (+1 for the empty space)
            else:   # a new document (or "sentence") has started
                data_dict['content'] = s    # the content is the sentence
                s = ''  # new sentence starts
                """annotation = []
                # is a list of dictionaries of form {label: label, points: [{text : word, start : start, end : end}]}
                for lab in list(label_dict.keys()): # for every label (that is attached to words and indices)
                    for i in range(len(label_dict[lab])):   # has form of list of dictionaries in form we want!
                        annotation.append(label_dict[lab][i])   # this should give us the annotation we want"""
                label_list = [] # initiate empty label list?
                for ents in list(label_dict.keys()):    # for all the labels in the list (which are attached to words)
                    for i in range(len(label_dict[ents])):  # loop over all the words in one label
                        if label_dict[ents][i]['text'] != '':   # text not empty (why would it be though?)
                            l = [ents, label_dict[ents][i]]
                            for j in range(i + 1, len(label_dict[ents])):
                                if (label_dict[ents][i]['text'] == label_dict[ents][j]['text']):
                                    di = {}
                                    di['start'] = label_dict[ents][j]['start']
                                    di['end'] = label_dict[ents][j]['end']
                                    di['text'] = label_dict[ents][i]['text']
                                    l.append(di)
                                    label_dict[ents][j]['text'] = ''
                            label_list.append(l)

                for entities in label_list:
                    label = {}
                    label['label'] = [entities[0]]
                    label['points'] = entities[1:]
                    annotations.append(label)
                data_dict['annotation'] = annotations
                annotations = []
                json.dump(data_dict, fp)
                fp.write('\n')
                data_dict = {}
                start = 0
                label_dict = {}
    except Exception as e:
        logging.exception("Unable to process file" + "\n" + "error = " + str(e))
        return None

def join_hyphenated_tokens(df):
    """Remove hyphens and merge tokens that were split at the end of a line in an article"""
    # Remove the hyphen in the last row if needed
    if df.tail(1).TOKEN.any() == '¬':
        df.drop(df.tail(1).index, inplace=True)
    
    print(df.info())
    indexes_to_remove = []
    for index, row in df.iterrows():
        if row.TOKEN == '¬':
            # Get token above
            token_half_1 = df.iloc[index-1].TOKEN
            # Get token below
            token_half_2 = df.iloc[index+1].TOKEN
            # Tag '¬' and second half for removal
            indexes_to_remove.append(index)
            indexes_to_remove.append(index+1)
            # Update the first half row token value
            df.at[index-1, 'TOKEN'] = token_half_1 + token_half_2

    df.drop(indexes_to_remove, inplace=True)

def preprocess(dfs):
    """Start the preprocessing pipeline for the document dataframes"""
    for dataframe in dfs:
        # Remove crochets '¬'
        join_hyphenated_tokens(dataframe)

if __name__ == "__main__":
    # Get data file
    data_file = open(DATA_FILE_PATH, "r")
    # Create dataframes
    dataframes = DataframeCreator().create_dataframes(data_file)
    # Preprocessing pipeline
    preprocess(dataframes)
    


    


