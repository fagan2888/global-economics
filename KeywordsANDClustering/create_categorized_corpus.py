import os, sys, re, csv
import heapq
import string
import gensim
import itertools
import json
from operator import itemgetter
import nltk
from nltk import *
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.corpus.reader import CategorizedPlaintextCorpusReader

# Using csv file with correct names matrhing original ones (from json file)
# Creates dictionary that could be mapped further
def get_correct_names():
    ndct = {}
    with open('/Users/dariaulybina/Desktop/global-economics-master/country_match.csv', 'r', encoding='latin1') as f:
        reader = list(csv.DictReader(f))
        for row in reader:
            dct = {
            row['origin']:row['destination']
            }
            ndct.update(dct)
    return ndct

#create the regex for tagging
def tags_assignment(data): 
    fiscal = re.compile(r'\bfiscal|\bpublic|\btax|\bdebt\s+sustainability',flags=re.I)
    mon = re.compile(r'\bmonetary|\binterest',flags=re.I)
    fin = re.compile(r'\bfinancial|prudential',flags=re.I)
    rea = re.compile(r'\bproperty|economic|\bincome|\bdomestic|\binfrastructure|employment|\bstructural|\bgrowth|\bprivate|\blabor',flags=re.I)
    context = re.compile(r'\bcontext|\brecent|\boutlook\w*|\bpolicy\s+discussion|\bbackground|\bintro\w*|\bmarket|\bbank\w*|\bhousing|\bspillover',flags=re.I)
    risk = re.compile(r'\brisk\w*',flags=re.I)
    external = re.compile(r'\bexternal\w*',flags=re.I)
    exchange = re.compile(r'\bexchange|\bpeg',flags=re.I)
    evrth = []
    maindict = {}
    for d in data:
        cont = d['content']
        naming = d['doc']
        cou = d['country']
        if cou == 'PEOPLE’S REPUBLIC OF CHINA—HONG KONG SPECIAL ADMINISTRATIVE REGION':
            country = 'Hong Kong'
        elif cou == "PEOPLE'S REPUBLIC OF CHINA–MACAO ":
            country = "Macao"
        elif cou == 'Democratic-Republic-of-Sao-Tomé-and-Principe':
            country = "Sao Tome and Principe"
        else:
            countr = ndct[cou]
            countr = countr.replace('.','').replace('-','')
            country = re.sub('\s+','_',countr)
        y= d['year']
        year = y.replace('-','')
        for c in range(0,len(cont)):
            header = cont[c]['head']
            print(header)
            f=re.search(fiscal,header)
            m=re.search(mon,header)
            fi=re.search(fin,header)
            real=re.search(rea,header)
            con=re.search(context,header)
            risks=re.search(risk,header)
            extern=re.search(external,header)
            exch=re.search(exchange,header)
            if f: 
                Tag = 'Fiscal'
            elif m or exch:
                Tag = 'Monetary'
            elif fi:
                Tag = 'Financial'
            elif real:
                Tag = 'Real'
            elif risks:
                Tag = 'Risks'
            elif con:
                Tag = 'Context'
            elif extern:
                Tag = 'External'
            else:
                Tag = "Other"
            taglist = []
            taglist.append(Tag)
            print("Tail : {}".format(cont[c]['tail']))
            text = cont[c]['tail']
            if len(text)>0:
                key = naming+"_"+str(c)+".txt"
                key2 = country+ year +"_"+str(c)+".txt"
                newdict = {
                key2: taglist
                }
                maindict.update(newdict)
                dict1 = {'key1': key,
                'key2': key2,
                'header': header,
                'country':country,
                'year':year,
                'text':text,
                'tag': Tag
                }
                evrth.append(dict1)
                c = c + 1
            else:
                print("skip")
                c = c + 1
                #print(''.join([i for i in evrth[i]['country']]))
                #print(maindict['-doc-cr17325.txt'])
    return evrth, maindict

def get_data():
    path1 = '/Users/dariaulybina/Desktop/global-economics-master/Final2.json'
    with open(path1) as datafile:
        data = json.load(datafile)
        datafile.close()
    return data

def create_corpus(evrth):
    corpusdir = '/Users/dariaulybina/Desktop/global-economics-master/corpusCategory/'
    #Make new dir for the corpus.
    if not os.path.isdir(corpusdir):
        os.mkdir(corpusdir)
    #Output the files into the directory
    i=0
    for i in range(0,len(evrth)):
        filename=evrth[i]['key2']
        #print(filename)
        with open(os.path.join(corpusdir,filename),'w') as fout:
            fout.write(evrth[i]['text'])
        i = i + 1
    return

################################
ndct = get_correct_names()

data = get_data()
print(len(data))
evrth, maindict = tags_assignment(data)

# Save new final dictionary as well as the mapping for categories-numbers
listingssss = json.dumps(evrth)
with open("FinalCleanJuly1.json","w") as f:
    f.write(listingssss)
dictionaries = json.dumps(maindict)
with open("CorpusCatMapJuly1.json","w") as f:
    f.write(dictionaries)

#### This is IMPORTANT - CHOOSE ! ##### default is key2
#### Choose the label you want to have for naming!
### two options: 
### 1) key1 with format: docID + _(i) where i numerated number of category e.g. -doc-_cr14021.txt
### 2) key2 with format country name + year + _(i) e.g. Albania2015_1.txt
### if you want to change--> line 90: "key2: taglist" to key1 
### line 121: filename=evrth[i]['key2'] to key1
create_corpus(evrth)

#### Check if working
reader = CategorizedPlaintextCorpusReader('corpusCategory/', r'\w+\d+_.*\.txt', cat_map=maindict)
print(reader.categories()) #print all categories in a list
print(reader.fileids(categories=['Fiscal'])) #check docIDs in fiscal category


#Good reference - https://www.packtpub.com/books/content/python-text-processing-nltk-20-creating-custom-corpora
#They have options for creating chunked (by words, sentences, paragraphs and even customized paragraphs) corpora, tagged corpora etc
