from syntok.tokenizer import Token, Tokenizer
import syntok.segmenter as segmenter
from typing import Iterator, List
from .spacy_converter import Converter


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
        while sentence:
            if sentence.startswith(" "):
                char_index += 1
                # Remove the whitespace
                sentence = sentence[1:]
                continue

            _, row = next(df_gen)
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


    def segment_sentences(self, dataframe):
        """ 
        Segment the sentences of a dataframe and provide metadata for each token. 
        
        Returns:
            [(string, (int, int), string)]: list of (token, (start_index, end_index), NER_tag)
            [string]: sentences
        """
        # Create a String from the dataframe tokens
        document_text = Converter().text_from_dataframe_tokens(dataframe)
        # Get sentences
        sentences = self._create_sentences_from_text(document_text)
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
