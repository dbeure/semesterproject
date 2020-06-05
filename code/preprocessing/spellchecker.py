from symspellpy import SymSpell, Verbosity
from wikidata.client import Client
from wikidata.datavalue import DatavalueError
from syntok.tokenizer import Tokenizer
from Levenshtein import distance
import re

class Spellchecker:
    """The class responsible for token spellchecking"""
    MAX_EDIT_DISTANCE = 3
    MAX_LEVENSHTEIN_DISTANCE = 4

    def __init__(self, dictionary_path):
        """
        Args:
            dictionary_path (str): the path of the token frequency dict
        """
        self.sym_spell = SymSpell(
            max_dictionary_edit_distance=Spellchecker.MAX_EDIT_DISTANCE,
        )

        loaded = self.sym_spell.load_dictionary(
            dictionary_path, term_index=0, count_index=1, separator=" "
        )
        assert(loaded)
        print("Loaded SymSpell dictionary.")

    def _replace_in_df(self, df, to_replace, value):
        df["TOKEN"] = df["TOKEN"].str.replace(to_replace, value)

    def manual_spellcheck(self, df):
        """
        Manual spellcheck that looks for KNOWN and repeatable patterns 
        in the data that can be replaced by a correct token/word.

        Args:
            df (pandas.Dataframe): the dataframe that will get spellchecked
        """
        self._replace_in_df(df, "jebesmal", "jedesmal")
        self._replace_in_df(df, "Thatsache", "tat")
        self._replace_in_df(df, "Giengen", "gingen")
        self._replace_in_df(df, "Gcgenthcrl", "Gegenteil")
        self._replace_in_df(df, "\? unastie", "Dynastie")
        self._replace_in_df(df, "L rnnburg", "Luxemburg")
        self._replace_in_df(df, "Jstzt", "jetzt")
        self._replace_in_df(df, "Glaubensbekcnntniß", "Glaubenbekenntniss")
        self._replace_in_df(df, "T u r i n", "Turin")
        self._replace_in_df(df, "nöthicM", "nötigen")

    def automated_spellcheck(self, df):
        """
        Automated spellcheck that looks for unpredictable OCR errors in the
        data and replaces them with hopefully correct tokens.

        Args:
            df (pandas.Dataframe): the dataframe that will get spellchecked
        """
        wikidata_client = Client()
        tokenizer = Tokenizer(replace_not_contraction=False)
        ignore_regex_str = "^[0-9.!?*„_\-\—,;:<>='|\[\]\"()^«»/°•©>]+"
        ignore_regex = re.compile(ignore_regex_str)

        for index, row in df.iterrows():
            # Get the token
            token = row["TOKEN"]
            wiki_metadata = row["NEL-LIT"]

            # Autocorrect 
            suggestions = self.sym_spell.lookup(
                token, Verbosity.TOP, transfer_casing=True, 
                include_unknown=True, ignore_token=ignore_regex_str,
                max_edit_distance=Spellchecker.MAX_EDIT_DISTANCE
            )
            # Save the first suggestion if we have one
            if suggestions and suggestions[0].term != token.lower():
                if wiki_metadata.startswith('Q'):
                    # 1. 'Qxxxx' - Use the Wikidata column value to spellcheck
                    if ignore_regex.match(token):
                        # token should be ignored 
                        continue

                    wikidata_entity = wikidata_client.get(wiki_metadata)
                    try:
                        wikidata_label = wikidata_entity.attributes['labels']['de']['value']
                    except KeyError:
                        # the wikidata has no 'de' entry for the label, ignore spellcorrection
                        continue
                    
                    wikidata_labels = tokenizer.tokenize(wikidata_label)
                    wikidata_labels = map(lambda t: t.value, wikidata_labels)
                    wikidata_labels = filter(lambda t: not ignore_regex.match(t), wikidata_labels)
                    wikidata_labels = list(wikidata_labels)

                    # Check if the token is not an abbreviation
                    is_abbreviation = False
                    for sublabel in wikidata_labels:
                        if sublabel.startswith(token):
                            print(token, "(abbrev) ->", sublabel,  " | ", wiki_metadata)
                            df.at[index, 'TOKEN'] = sublabel
                            is_abbreviation = True
                            break
                    
                    if is_abbreviation:
                        continue
                            
                    
                    try:
                        best_match = sorted(wikidata_labels, key=lambda t: distance(t, token))[0]
                    except IndexError:
                        continue

                    if distance(best_match, token) <= Spellchecker.MAX_LEVENSHTEIN_DISTANCE:
                        print(token, "(best_match) ->", best_match,  " | ", wiki_metadata)
                        df.at[index, 'TOKEN'] = best_match
                else:
                    # 2. 'NIL' / '_' - Use symspell
                    suggestion = suggestions[0].term
                    print(token, "(symspell) ->", suggestion, " | ", wiki_metadata)
                    df.at[index, 'TOKEN'] = suggestion

            
                

            
