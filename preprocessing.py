# -*- coding: utf-8 -*-


import spacy
import csv
import pandas as pd
from itertools import islice

def preprocess(tok):
    tok = tok.lower()
    tok = tok.replace('y', 'i')  # no standard between i and y
    tok = tok.replace('th', 't')  # no standard between th and t
    tok = tok.replace('ie', 'i')  # frequently in older sources, installirt or situirt statt iert
    if tok != 'des' and tok.endswith('es'):  # should get rid of the Genitiv, might get rid of french words
        tok = tok[:-2]
    tok = tok.replace('ä', 'a') #for german non-standardized ä, ae and a
    tok = tok.replace('ae', 'a')
    tok = tok.replace('ö', 'o') #same for ö
    tok = tok.replace('oe', 'o')
    tok = tok.replace('ü', 'u') #same for ü
    tok = tok.replace('ue', 'u')
    return tok

reader = csv.reader(open('HIPE-test.tsv', encoding='ISO-8859-1'), delimiter='\t')
#df = pd.DataFrame(reader)


TRAIN_DATA = []

#will try this whole thing with an iter() later on
indices = []    # is the list of indices at which there are NE
labels = []
NE_tag= []
words = []
sentence = ''
j = 0 #j is the index of letters

for row in islice(reader, 9, None): #makes same as writing next(reader, None) 8 times!
    if len(row) <= 1:
        if row[0].startswith('#'):
            pass    #will have to check with the line commencing with # and stuff
        else:
            pass
    elif len(row) > 1 and row[0] != 'TOKEN':
        token = row[0]
        tag = row[1]
        token = preprocess(token)
        print(token, tag)
        sentence = sentence + token + ' '
        if tag == 'O':
            j += len(token)+1 #needs an empty space every time to fit the content
        if tag.startswith('B') or tag.startswith('I'):
            if tag not in labels :
                labels.append(tag)
            x1 = j
            j += len(token) + 1
            NE_tag.append(tag)
            words.append(token)
            x2 = x1+len(token)
            indices.append((x1, x2))
        if token == "\\'ac":
            #take last token, sentences at this point looks like this : "bla bla bla this \'ac "
            last_tok = sentence.split()[-2]
            #take next token
            next_line = next(reader, None)  #because the one just after is separator starting with an #
            good_line = next(reader, None)
            next_tok = good_line[0]
            next_tag = good_line[1] #necessary?
            #append the two
            last_tok = last_tok+next_tok
            #update all info: indices, j, word and sentence. NE_tag remains the same!
            last_index = indices[-1]
            new_last_index = (last_index[0], last_index[1]+len(next_tok))
            indices[-1] = new_last_index
            j += len(next_tok) #no need for space as it was already there
            words[-1] = last_tok
            sentence = sentence[:-6]+next_tok+' '
            #make next token be an empty string, with 0 as tag
            good_line[0] = ''
            good_line[1] = ''
        if token == '.':    #token is a point means end of a sentence, it puts everything in the json format and reinitiates
            TRAIN_DATA.append((sentence, {'entities': [(z, x[0], x[1], y) for z, x, y in zip(words, indices, NE_tag)]}))
            sentence = ''
            indices = []
            NE_tag = []
            words = []






print(indices)
print(NE_tag)
print(sentence)

print(TRAIN_DATA)
print(labels)

string = "bla bla bla this \'ac "
print(string.split()[-2])



"""name = ['Debora', 'Beuret']
namen = 'Debora Beuret'
namestring = ''
j = 0
for i in range (2):
    nam = name[i]
    j += len(nam) + 1
    namestring = nam + ' '
    end = 7 + len(name[1])
print(namen[7:14])"""









