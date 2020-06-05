from .sentence_segmenter import SentenceSegmenter
from .spellchecker import Spellchecker
import pandas as pd

class Preprocessor:
    """Handles the preprocessing pipeline"""

    def _join_hyphenated_tokens(self, df):
        """
        Remove hyphens and merge tokens that were split at the end of a line.

        Example:
            'verste', '¬', 'hen' ~> 'verstehen' 

            The merged token ('verstehen') would have the metadata 
            (NER tags) of the first token ('verste').
        """
        # Remove the hyphen in the last row of the document if needed
        if df.tail(1).TOKEN.any() == '¬':
            df.drop(df.tail(1).index, inplace=True)
        
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

    def preprocess(self, dfs, path_to_freq_dict):
        """
        Start the preprocessing pipeline for the document dataframes.

        Args:
            dfs ([pandas.DataFrame]): list of DataFrames
            path_to_freq_dict (str): path to the german word frequency dictionary
        """
        segmenter = SentenceSegmenter()
        spellchecker = Spellchecker(path_to_freq_dict)
        
        preprocessed = []
        for dataframe in dfs:
            # 1. Remove crochets ('¬') and join the hyphenated tokens
            self._join_hyphenated_tokens(dataframe)
            # 2. Manual Spellcheck
            spellchecker.manual_spellcheck(dataframe)
            # 3. Automated Spellcheck
            # TODO: Move the automated spellcheck after the senetence 
            # segmentation?
            spellchecker.automated_spellcheck(dataframe)
            # 4. Segment into sentences
            segments = segmenter.segment_sentences(dataframe)
            preprocessed.append(segments)
        
        result_ner = []
        result_sentences = []
        for ner_data, sentences in preprocessed:
            result_ner += ner_data
            result_sentences += sentences

        return result_ner, result_sentences

    def preprocess_for_spacy_convert(self, dfs, path_to_freq_dict):
        """
        Start the preprocessing pipeline for the document dataframes. 
        Create a dataframe ready for use with `spacy convert` CLI command.

        Args:
            dfs ([pandas.DataFrame]): list of DataFrames
            path_to_freq_dict (str): path to the german word frequency dictionary
        """
        segmenter = SentenceSegmenter()
        spellchecker = Spellchecker(path_to_freq_dict)
        result = []
        for dataframe in dfs:
            # 0. Uppercase NER tags
            ner_col = 'NE-COARSE-LIT'
            dataframe[ner_col] = dataframe[ner_col].str.upper()
            # 1. Remove crochets ('¬') and join the hyphenated tokens
            self._join_hyphenated_tokens(dataframe)
            # 2. Manual Spellcheck
            spellchecker.manual_spellcheck(dataframe)
            # 3. Automated Spellcheck
            # TODO: Move the automated spellcheck after the senetence 
            # segmentation?
            #spellchecker.automated_spellcheck(dataframe)
            # 4. Segment into sentences
            segmented = segmenter.segment_sentences_to_dataframes(
                dataframe
            )
            result.append(segmented)

        return result
