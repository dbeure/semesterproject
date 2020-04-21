#!/usr/bin/env python
# coding: utf8

from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

file = open('../data/preprocessed/train_doc_0', 'r')


#TRAIN_DATA = [
#    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
#    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
#]

TRAIN_DATA = [("Der Umkreisdes neuen Nationalpallasies der 500, dem Antritt der Revolutionsbrücke gegenüber am Seineufergelegen, enthält gegen Norden den Quai d'Orsai bis zur Nationalbrücke, den Platz dela Concorde bis zur Orangerie, längs der Gebäude du Gardemeuble an den elyseischen Feldern hin bis zum Anfange der Straße nach Versailles und dem die Esplanade der Invaliden von der Mauer um den Garten des Raths der 500 scheidet, vom Quai d'Orsai bis zur Universitätsgasse: gegen Südendiese Gasse bis zur Straße Courty; gegen Osten die Straße Bourgogne bis zum Quai d'Orsai In diesem Bezirke haben die Saalinspectoren die Polizeyaufsichtallein; doch kann die allgemeine Polizey Dee",
               {'entities': [(21, 38, 'B-loc'), (64, 81, 'B-loc'), (95, 104, 'B-loc'), (138, 142, 'B-loc'), (143, 144, 'I-loc'), (144, 145, 'I-loc'), (145, 150, 'I-loc'), (159, 173, 'B-loc'), (179, 184, 'B-loc'), (185, 189, 'I-loc'), (190, 198, 'I-loc'), (207, 216, 'B-loc'), (228, 235, 'B-loc'), (236, 238, 'I-loc'), (239, 250, 'I-loc'), (314, 324, 'B-loc'), (337, 346, 'B-loc'), (347, 350, 'I-loc'), (351, 360, 'I-loc'), (393, 398, 'B-org'), (399, 402, 'I-org'), (403, 406, 'I-org'), (421, 425, 'B-loc'), (426, 427, 'I-loc'), (427, 428, 'I-loc'), (428, 433, 'I-loc'), (442, 459, 'B-loc'), (492, 498, 'B-loc'), (499, 505, 'I-loc'), (523, 529, 'B-loc'), (530, 539, 'I-loc'), (548, 552, 'B-loc'), (553, 554, 'I-loc'), (554, 555, 'I-loc'), (555, 560, 'I-loc')]})]



def main(model=None, output_dir=None, n_iter=100):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])   #add label

    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        # reset and initialize the weights randomly – but only if we're
        # training a new model
        if model is None:
            nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == "__main__":
    plac.call(main)


