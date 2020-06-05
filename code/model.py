#!/usr/bin/env python
# coding: utf8

from __future__ import unicode_literals, print_function

import os
import plac
import json
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

BASEDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
PREPROCESSED_FILE_PATH = os.path.join(BASEDIR, 'data/preprocessed/train_doc.json')
data_file = open(PREPROCESSED_FILE_PATH, 'r')
TRAIN_DATA = json.load(data_file)

def main(output_dir=None, n_iter=25):
    """Load the model, set up the pipeline and train the entity recognizer."""
    # Load the spacy-big pre-trained model
    # https://spacy.io/models/de#de_core_news_md
    model_name = "de_core_news_md"
    print("Loading '{}'".format(model_name))
    nlp = spacy.load(model_name) 
    print("Loaded '{}' model".format(model_name))

    ner = nlp.get_pipe("ner")

    print("Default labels:", ner.labels)
    # Add labels
    for j_doc in TRAIN_DATA:
        print(j_doc.get("id"), j_doc.get("paragraphs"))
        for paragraph in j_doc.get("paragraphs"):
            for sentence in paragraph.get("sentences"):
                for token in sentence.get("tokens"):
                    ner_tag = token.get("ner")
                    if ner_tag != 'O':
                        label = ner_tag.split("-")[1]
                        ner.add_label(label)
    print("Labels:", ner.labels)
    print("Entities:", ner.move_names)


    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                para_golds = []
                for sample in batch:
                    para_text = []
                    para_ner = []
                    for paragraph in sample.get("paragraphs"):
                        for sentence in paragraph.get("sentences"):
                            for token in sentence.get("tokens"):
                                para_text.append(token.get("orth"))
                                para_ner.append(token.get("ner"))
                    para_golds.append(dict(words=para_text, entities=para_ner))
                nlp.update(
                    docs=None,
                    golds=para_golds,
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


if __name__ == "__main__":
    plac.call(main)


