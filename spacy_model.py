#!/usr/bin/env python
# coding: utf8
#authors : David Bielik and Debora Beuret, based on:
# https://towardsdatascience.com/custom-named-entity-recognition-using-spacy-7140ebbb3718

# Training additional entity types using spaCy
from __future__ import unicode_literals, print_function
import pickle
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

LABEL = ['B-loc', 'B-pers', 'I-pers', 'B-org', 'I-org', 'I-loc']
TRAIN_DATA = [('frankreich . ', {'entities': [('frankreich', 0, 10, 'B-loc')]}), ('gesetzgeber . ', {'entities': []}), ('den 19 . ', {'entities': []}), ('niv . ', {'entities': []}), ('( 8 . ', {'entities': []}), ("j\\'e4n . ", {'entities': []}), (") ward di staatskleidung der sekret\\'e4r - redacteurs , der staatsboten und torw\\'e4chter f\\'fcr beide r\\'e4te bestimmt . ",{'entities': []}), ("auf talot ' s vorschlag beschlo\\'df man \\'fcber den constitutionellen umkreis , welchen das gesetzgebende corps in zukunft inne haben soll , folgendes : vom tage an , da der rat der 500 in seinen neun pallast installirt sein wird , sind di \\'e4u\\'dferlichen bezirke f\\'fcr beide r\\'e4te folgendermassen firir : rarh der alten : der umfang des nationalpallastes der alten , in den tuillerin situirt , enh\\'e4lt gegen westen di stra\\'dfe und den platz des carrousel bis zum eintritt in di stra\\'dfe nicaise , am hause coigni vorbei bis zur stra\\'dfe des orties , di passage de marigni mit einbegriffen : gegen suden den teil des quai der gallerin des louvre ' s von der passage de marigni am rechten ufer der seine hinab bis zum quai der tuilerin , vom rechten winkel des parapets bei der nationalbrucke bis an den eingang zum platze de la coneorde , di nationalbr\\'fccke bis zum quai voltaire mit einbegriffen ; gegen osten den platz de la concorde in gemeinschaft mit dem rate der 500 : gegen norden den hof der orangeri , di passage des feuillans , di casernen der grenadirs des gesetzg . ", {'entities': [('talot', 183, 188, 'B-pers'), ("'", 189, 190, 'I-pers'), ('folgendes', 191, 198, 'I-pers'), ('rat', 358, 361, 'B-org'), ('der', 362, 365, 'I-org'), ('folgendermassen', 366, 375, 'I-org'), ('rarh', 505, 509, 'B-org'), ('der', 510, 513, 'I-org'), ('nationalpallastes', 514, 534, 'I-org'), ('tuillerin', 579, 588, 'B-loc'), ('platz', 643, 648, 'B-loc'), ('des', 649, 652, 'I-loc'), ('carrousel', 653, 662, 'I-loc'), ("stra\\'dfe", 686, 695, 'B-loc'), ('nicaise', 696, 703, 'I-loc'), ('hause', 709, 714, 'B-loc'), ('coigni', 715, 721, 'I-loc'), ("stra\\'dfe", 737, 746, 'B-loc'), ('des', 747, 750, 'I-loc'), ('or', 751, 753, 'I-loc'), ('orties', 754, 762, 'I-loc'), ('passage', 768, 775, 'B-loc'), ('de', 776, 778, 'I-loc'), ('gegen', 779, 789, 'I-loc'), ('quai', 836, 840, 'B-loc'), ('der', 841, 844, 'I-loc'), ('gallerin', 845, 853, 'I-loc'), ('des', 854, 857, 'I-loc'), ('louvre', 858, 864, 'I-loc'), ("'", 865, 866, 'I-loc'), ('s', 867, 868, 'I-loc'), ('passage', 877, 884, 'B-loc'), ('de', 885, 887, 'I-loc'), ('marigni', 888, 895, 'I-loc'), ('seine', 916, 921, 'B-loc'), ('quai', 936, 940, 'B-loc'), ('der', 941, 944, 'I-loc'), ('tuilerin', 945, 953, 'B-loc'), ('national', 996, 1004, 'B-loc'), ('nationalbrucke', 1005, 1015, 'I-loc'), ('platze', 1039, 1045, 'B-loc'), ('de', 1046, 1048, 'I-loc'), ('la', 1049, 1051, 'I-loc'), ('con', 1052, 1055, 'I-loc'), ('coneorde', 1056, 1065, 'I-loc'), ("nationalbr\\'fccke", 1071, 1088, 'B-loc'), ('quai', 1097, 1101, 'B-loc'), ('voltaire', 1102, 1110, 'B-pers'), ('platz', 1146, 1151, 'B-loc'), ('de', 1152, 1154, 'I-loc'), ('la', 1155, 1157, 'I-loc'), ('con', 1158, 1161, 'I-loc'), ('concorde', 1162, 1171, 'I-loc'), ('rate', 1196, 1200, 'B-org'), ('der', 1201, 1204, 'I-org'), ('gegen', 1205, 1211, 'I-org'), ('hof', 1233, 1236, 'B-loc'), ('der', 1237, 1240, 'I-loc'), ('orangeri', 1241, 1249, 'I-loc'), ('passage', 1255, 1262, 'B-loc'), ('des', 1263, 1266, 'I-loc'), ('feuillans', 1267, 1276, 'I-loc')]})]

model = None    #no model to start with
n_iter = 100    #start with 100 iterations, just to see how script runs

#Create a SpaCy model:
nlp = spacy.blank('de')  # create blank Language class
print("Created blank 'de' model")

# Add entity recognizer to the pipeline if not there
if 'ner' not in nlp.pipe_names:
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner)
else:
    ner = nlp.get_pipe('ner')

# Add new entity labels to entity recognizer
for i in LABEL:
    ner.add_label(i)

# Initializing optimizer
if model is None:
    optimizer = nlp.begin_training()
else:
    optimizer = nlp.entity.create_optimizer()

# Get names of other pipes to disable them during training to train # only NER and update the weights
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):  # only train NER
    for itn in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA,
                            size=compounding(4., 32., 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            # Updating the weights
            nlp.update(texts, annotations, sgd=optimizer,
                       drop=0.35, losses=losses)
            print('Losses', losses)
            nlp.update(texts, annotations, sgd=optimizer,
                       drop=0.35, losses=losses)
            print('Losses', losses)


