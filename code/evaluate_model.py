from __future__ import unicode_literals, print_function

import os
import plac
import json
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from spacy.scorer import Scorer
from spacy.gold import GoldParse

BASEDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

def score_on_split(ner_model, split):
    data_file_path = os.path.join(BASEDIR, 'data/preprocessed/{}_doc'.format(split))
    data_file = open(data_file_path, 'r')
    eval_data = json.load(data_file)

    scorer = Scorer()
    for input_, annot in eval_data:
        annot=annot['entities']
        doc_gold_text = ner_model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annot)
        pred_value = ner_model(input_)
        print("Prediction", [(ent.text, ent.label_) for ent in pred_value.ents], "|", "Gold", gold.ner)
        scorer.score(pred_value, gold)
    print("Scores for:", split)
    print("\tprecision:", scorer.ents_p, "\trecall:", scorer.ents_r, "\tF1", scorer.ents_f)
    print("\tper-type:", scorer.scores['ents_per_type'], "\n")

def main(model_path=("model/", 'option', 'r')):
    ner_model = spacy.load(model_path)  # load existing spaCy model
    print("Loaded model '%s'" % model_path)

    score_on_split(ner_model, "train")
    score_on_split(ner_model, "dev")

    


if __name__=="__main__":
    plac.call(main)