from syntok.tokenizer import Token, Tokenizer
import syntok.segmenter as segmenter
from typing import Iterator, List
from .spacy_converter import Converter
import re
import numpy as np


class SentenceSegmenter:

    def _analyze(self, document: str, bracket_skip_len=None) -> Iterator[Iterator[List[Token]]]:
        tok = Tokenizer(replace_not_contraction=False, emit_hyphen_or_underscore_sep=True)

        for offset, paragraph in segmenter.preprocess_with_offsets(document):
            tokens = tok.tokenize(paragraph, offset)
            yield segmenter.segment(tokens, bracket_skip_len)

    def _create_sentences_from_text(self, text):
        """ 
        Segment the sentences from a text input.
        
        Returns:
            [string]: sentences
        """
        sentences = []
        for paragraph in self._analyze(text):
            for sentence in paragraph:
                first_token = True
                sentence_text = ""
                for token in sentence:
                    if first_token:
                        sentence_text += token.value
                        first_token = False
                    else:
                        sentence_text += token.spacing + token.value

                sentences.append(sentence_text)

        return sentences

    def _remove_prefix(self, text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    def _get_char_start_end_indices(self, sentence, df_gen):
        """
        Compute starting and ending indices of the tokens inside a sentence.

        Args:
            sentence (string): -
            df_gen (generator): iterator for the rows of the dataframe
        
        Returns:
            char_indices: tuples of (start_index, end_index) for each token in a sentence
            nr_tokens: number of tokens
        """
        char_indices = []
        char_index = 0
        tokens, tags = [], []
        original_sentence = sentence
        while sentence:
            if sentence.startswith(" "):
                char_index += 1
                # Remove the whitespace
                sentence = sentence[1:]
                continue
            try:
                _, row = next(df_gen)
            except StopIteration:
                print(original_sentence)
                print(sentence)
            token = row.TOKEN
            tokens.append(token)
            tags.append(row['NE-COARSE-LIT'])
            
            if sentence.startswith(token):
                token_length = len(token)
                token_indices = (char_index, char_index + token_length)
                char_indices.append(token_indices)
                char_index += token_length
                sentence = sentence[token_length:]
        return tokens, char_indices, tags

    def _replace_dots_with_dottags(self, df):
        """
        Replace all '.' chars in tokens which are not just '.' by '<DOT>'
        """
        df["TOKEN"] = df["TOKEN"].str.replace(r"^(\w+)\.(\w+)$", r"\1<DOT>\2")
        

    def _replace_dottags_with_dots(self, sentences):
        """
        Replace all '<DOT>' substrings with '.' 
        """
        return [re.sub(r"<DOT>", ".", sentence) for sentence in sentences]

    def segment_sentences(self, dataframe):
        """ 
        Segment the sentences of a dataframe and provide metadata for each token. 
        
        Returns:
            [(string, (int, int), string)]: list of (token, (start_index, end_index), NER_tag)
            [string]: sentences
        """
        sentence_segmenter_df = dataframe.copy()
        # Replace '.' with '<DOT>'
        self._replace_dots_with_dottags(sentence_segmenter_df)
        # Create a String from the dataframe tokens
        document_text = Converter().text_from_dataframe_tokens(
            sentence_segmenter_df
        )
        # Get sentences
        sentences = self._create_sentences_from_text(document_text)
        # Replace '<DOT>' with '.'
        sentences = self._replace_dottags_with_dots(sentences)
        # Create the dataframe generator
        df_gen = dataframe.iterrows()
        sentences_metadata = []
        for sentence in sentences:
            tokens, char_indices, tags = self._get_char_start_end_indices(
                sentence, df_gen
            )
            sentence_metadata = list(zip(tokens, char_indices, tags))
            sentences_metadata.append(sentence_metadata)
        return sentences_metadata, sentences

    def segment_sentences_to_dataframes(self, dataframe):
        """ 
        Segment the sentences of a dataframe and return a list of dataframes where
        each dataframe is a sentence.
        
        Returns:
            [pandas.DataFrame]: the updated dataframe with a new MISC-SENT column
            [string]: list of sentences
        """
        sentence_segmenter_df = dataframe.copy()
        # Replace '.' with '<DOT>'
        self._replace_dots_with_dottags(sentence_segmenter_df)
        # Create a String from the dataframe tokens
        document_text = Converter().text_from_dataframe_tokens(
            sentence_segmenter_df
        )
        # Get sentences
        sentences = self._create_sentences_from_text(document_text)
        # Replace '<DOT>' with '.'
        sentences = self._replace_dottags_with_dots(sentences)
        # Create the dataframe generator
        df_gen = dataframe.iterrows()
        end_of_sentence_idxs = []
        current_index = 0
        for sentence in sentences:
            while sentence:
                if sentence.startswith(" "):
                    # remove whitespace
                    sentence = sentence[1:]
                    continue
                _, row = next(df_gen)
                token = row["TOKEN"]
                if sentence.startswith(token):
                    sentence = sentence[len(token):]
                    current_index += 1
                else:
                    raise Exception("Unexpected character in sentence: {}".format(sentence))
            end_of_sentence_idxs.append(current_index)
            current_index += 1
        return np.split(dataframe, end_of_sentence_idxs), sentences