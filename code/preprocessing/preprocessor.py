from .sentence_segmenter import SentenceSegmenter

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

    def preprocess(self, dfs):
        """Start the preprocessing pipeline for the document dataframes"""
        segmenter = SentenceSegmenter()
        
        result = []
        for dataframe in dfs:
            # 1. Remove crochets ('¬') and join the hyphenated tokens
            self._join_hyphenated_tokens(dataframe)
            # 2. Segment into sentences
            segments = segmenter.segment_sentences(dataframe)
            result.append(segments)
        return result
        