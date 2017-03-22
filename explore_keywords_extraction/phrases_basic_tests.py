# -*- coding: utf-8 -*- 
import nltk
from collections import Counter
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import string
import os, csv, sys, re
from nltk.collocations import *
#from sklearn.feature_extraction.text import TfidfVectorizer
nltk.download('stopwords')

def get_tokens(text):
    wordnet_lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(text.lower().translate(str.maketrans('','',string.punctuation)))
    lemmas = []
    for t in tokens:
        lemmas.append(wordnet_lemmatizer.lemmatize(t))
    return lemmas

def get_outputs(tokens_nlist):
    tok_list = [j for i in tokens_nlist for j in i]
    count1 = Counter(tok_list)
    print('20 most common lemmas: {}'.format(count1.most_common(50)))
    filtered = [w for w in tok_list if not w in stopwords.words('english')]
    count = Counter(filtered)
    print('50 most common lemmas without stopwords: {}'.format(count.most_common(50)))
    return filtered
    
def bigrams_with_gensim(data):
    from gensim.models import Phrases
    bigram = Phrases()
    sentences = []
    for row in data:
        title = row['Headings'].replace('[','').replace(']','').replace("'",'')
        title = title + '.'
        #title = title.replace('--',' -- ')
        sentence = [word for word in nltk.word_tokenize(title.lower())
                    if word not in string.punctuation]
        sentences.append(sentence)
        bigram.add_vocab([sentence])
    bigram_counter = Counter()
    for key in bigram.vocab.keys():
        if key not in stopwords.words("english"):
            spl = re.split(b'\_',key)
            spl = [s for s in spl if s !='']
            if len(spl) > 1:
                bigram_counter[key] += bigram.vocab[key]
    print('Bigrams with gensim')
    for key, counts in bigram_counter.most_common(50):
        print('{}: {}'.format(key, counts))
    return bigram

def bigrams_with_word2vec(data):
    from gensim.models import Phrases
    from gensim.models import Word2Vec
    bigram = Phrases()
    sentences = []
    for row in data:
        title = row['Headings'].replace('[','').replace(']','').replace("'",'')
        title = title + '.'
        sentence = [word for word in nltk.word_tokenize(title.lower())
                    if word not in string.punctuation]
        sentences.append(sentence)
        bigram.add_vocab([sentence])
    bigram_model = Word2Vec(bigram[sentences], size=100)
    bigram_model_counter = Counter()
    for key in bigram_model.wv.vocab.keys():
        if key not in stopwords.words("english"):
            spl = re.split('\_',key)
            spl = [s for s in spl if s !='']
            if len(spl) > 1:
                bigram_model_counter[key] += bigram_model.wv.vocab[key].count
    print('Bigrams with gensim.word2vec')
    for key, counts in bigram_model_counter.most_common(50):
        print('{}: {}'.format(key, counts))
    return bigram_model

'''def keywords_with_rake(stringing):
    import RAKE.RAKE as rake
    import operator
    
    rake_object = rake.Rake('/Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/GeneralTextStopList.txt')
    keywords = rake_object.run(stringing)
    print('First 50 Keywords: {}'.format(keywords[:50]))
    return keywords'''

######################################################################
if __name__ == "__main__":
    
    direct = '/Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/TEST_EXAMPLE_cr1601.csv'
    data = list(csv.DictReader(open(direct, encoding = 'utf-8', errors ='ignore')))

    rawTitles = []
    tokTitle = []
    sents = []
    for row in data:
        title = row['Headings'] + '.'
        titles = title.replace('[','').replace(']','').replace("'",'')
        sentence = [word for word in nltk.word_tokenize(titles.lower())
                        if word not in string.punctuation]
        sents.append(' '.join(sentence))
        tok = get_tokens(title)
        tokTitle.append(tok)
        rawTitles.append(titles)

# For comparison and test purposes, comment out tests you are not working with 

    '''For Most common Lemmas without stopwords'''
    stringing = '. '.join(rawTitles)
    filtered = get_outputs(tokTitle)

    '''For Gensim and bigrams extraction'''
    bgrm1 = bigrams_with_gensim(data)
    bgrm = bigrams_with_word2vec(data)
    bgrm.most_similar(positive=[‘fiscal_consolidation']) #not ideal for already extracted tags due to methodology used

    '''For Rake - TO BE FINALIZED - ISSUES'''
    #stringing = ' '.join(rawTitles)
    #kwd = keywords_with_rake(stringing)

    '''NLTK Bigram AssocMeasures'''
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()

    tokens = nltk.wordpunct_tokenize(rawTitles)    
    finder = BigramCollocationFinder.from_words(tokens)
    scored = finder.score_ngrams(bigram_measures.raw_freq)
    print(sorted(bigram for bigram, score in scored))
    finder.apply_freq_filter(4)
    print(finder.nbest(bigram_measures.pmi, 10))


