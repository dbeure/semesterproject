from symspellpy import SymSpell, Verbosity

class Spellchecker:
    """The class responsible for token spellchecking"""
    MAX_EDIT_DISTANCE = 2

    def __init__(self, dictionary_path):
        """
        Args:
            dictionary_path (str): the path of the token frequency dict
        """
        self.sym_spell = SymSpell(
            max_dictionary_edit_distance=Spellchecker.MAX_EDIT_DISTANCE,
        )

        self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

    def manual_spellcheck(self, df):
        """
        Manual spellcheck that looks for KNOWN and repeatable patterns 
        in the data that can be replaced by a correct token/word.

        Args:
            df (pandas.Dataframe): the dataframe that will get spellchecked
        """
        df["TOKEN"].replace("Jebesmal", "jedesmal")
        df["TOKEN"].replace("Thatsache", "tat")
        df["TOKEN"].replace("Giengen", "gingen")
        df["TOKEN"].replace("Gcgenthcrl", "Gegenteil")
        df["TOKEN"].replace("? unastie", "Dynastie")
        df["TOKEN"].replace("L rnnburg", "Luxemburg")
        df["TOKEN"].replace("Jstzt", "jetzt")
        df["TOKEN"].replace("Glaubensbekcnntniß", "Glaubenbekenntniss")
        df["TOKEN"].replace("T u r i n", "Turin")
        df["TOKEN"].replace("nöthicM", "nötigen")

    def automated_spellcheck(self, df):
        """
        Automated spellcheck that looks for unpredictable OCR errors in the
        data and replaces them with hopefully correct tokens.

        Args:
            df (pandas.Dataframe): the dataframe that will get spellchecked
        """
        for index, row in df.iterrows():
            # Get the token
            token = row["TOKEN"]
            # Autocorrect 
            suggestions = self.sym_spell.lookup(
                token, Verbosity.CLOSEST, transfer_casing=True, 
                include_unknown=True, ignore_token="^[0-9._,;:'\"()]+"
            )
            # Save the first suggestion
            if suggestions:
                print(token, suggestions[0].term)
                df.at[index-1, 'TOKEN'] = suggestions[0].term

            
