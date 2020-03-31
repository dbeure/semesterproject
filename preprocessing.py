import spacy
import csv
import pandas as pd

reader = csv.reader(open('HIPE-test.tsv'), delimiter='\t')
#df = pd.DataFrame(reader)


TRAIN_DATA = []

#will try this whole thing with an iter() later on
indices = []    # is the list of indices at which there are NE
NE_tag= []
words = []
sentence = ''
j = 0 #j is the index of letters
#for row in df.iterrows():    #i is the index of lines, the two first are irrelevant there
    #print(row)
    #token = row['TOKEN']
    #tag = row['NE-COARSE-LIT']
    #print(token, tag)
for row in reader:
    if len(row) == 1:
        if row[0].startswith('#'):
            pass    #will have to check with the line commencing with # and stuff
    elif len(row) > 1:
        token = row[0]
        tag = row[1]
        print(token, tag)
        sentence = sentence + token + ' '
        if tag == 'O':
            j += len(token)+1 #needs an empty space every time to fit the content
        if tag.startswith('B'):
            x1 = j
            j += len(token) + 1
            NE_tag.append(tag)
            words.append(token)
            x2 = x1+len(token)
            indices.append((x1, x2))
        if tag.startswith('I'):
            x1 = j
            j += len(token) + 1
            NE_tag.append(tag)
            words.append(token)
            x2 = x1 + len(token)
            indices.append((x1, x2))
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










