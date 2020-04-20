import re
from io import StringIO
import pandas as pd


class DataframeCreator:

    def _get_file_string_data(self, file):
        return file.read()

    def _split_metadata_line(self, string_data):
        """Return a tuple: (first_line, rest_of_data)"""
        return string_data.split("\n", 1)

    def _split_into_documents(self, corpus):
        """Split a corpus into multiple documents by a regex"""
        empty_line_pattern = re.compile("\n\n")
        return empty_line_pattern.split(corpus)

    def _create_dataframe_from_document(self, document):
        doc_handle = StringIO(document)
        return pd.read_csv(
            doc_handle,
            sep='\t',
            keep_default_na=False,      # treats 'null' as a string rather than a number while parsing
            skip_blank_lines=True,   
            comment="#",                # ignores lines starting with '#'
            quoting=3                   # handles quotes as tokens correctly
        )

    def create_dataframes(self, file):
        """Return dataframes for each document from the NER data corpus"""
        string_data = self._get_file_string_data(file)
        corpus_metadata, raw_corpus = self._split_metadata_line(string_data)
        documents = self._split_into_documents(raw_corpus)

        dataframes_list = []
        # Prepend the corpus metadata line to each document
        for index, document in enumerate(documents):
            documents[index] = corpus_metadata + document
            # Create the dataframe
            dataframe = self._create_dataframe_from_document(documents[index])
            dataframes_list.append(dataframe)

        return dataframes_list