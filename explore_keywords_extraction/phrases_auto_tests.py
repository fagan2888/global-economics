import nltk
from collections import Counter
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import string
import os, csv, sys, re
import itertools
import gensim
from pprint import pprint
from itertools import takewhile, tee
import networkx

def score_keyphrases_by_textrank(text, n_keywords=0.05):
    # tokenize for all words, and extract *candidate* words
    words = [word.lower()
             for sent in nltk.sent_tokenize(text)
             for word in nltk.word_tokenize(sent)]
    candidates = extract_candidate_words(text)
    # build graph, each node is a unique candidate
    graph = networkx.Graph()
    graph.add_nodes_from(set(candidates))
    # iterate over word-pairs, add unweighted edges into graph
    def pairwise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
    for w1, w2 in pairwise(candidates):
        if w2:
            graph.add_edge(*sorted([w1, w2]))
    # score nodes using default pagerank algorithm, sort by score, keep top n_keywords
    ranks = networkx.pagerank(graph)
    if 0 < n_keywords < 1:
        n_keywords = int(round(len(candidates) * n_keywords))
    word_ranks = {word_rank[0]: word_rank[1]
                  for word_rank in sorted(ranks.items(), key=lambda x: x[1], reverse=True)[:n_keywords]}
    keywords = set(word_ranks.keys())
    # merge keywords into keyphrases
    keyphrases = {}
    j = 0
    for i, word in enumerate(words):
        if i < j:
            continue
        if word in keywords:
            kp_words = list(takewhile(lambda x: x in keywords, words[i:i+10]))
            avg_pagerank = sum(word_ranks[w] for w in kp_words) / float(len(kp_words))
            keyphrases[' '.join(kp_words)] = avg_pagerank
            # counter as hackish way to ensure merged keyphrases are non-overlapping
            j = i + len(kp_words)
    result = sorted(keyphrases.items(), key=lambda x: x[1], reverse=True)
    return result

#Unsupervised Extraction 'Noun Phrases Only' - search for a pattern <<adjective -> noun -> proposition(optional) _> followed by another pair of adjective -> noun '

def extract_candidate_chunks(text, grammar=r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'):
    
    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    
    # tokenize, POS-tag, and chunk using regular expressions
    chunker = nltk.chunk.regexp.RegexpParser(grammar)
    tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))
    all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent))
                                                    for tagged_sent in tagged_sents))
    # join constituent chunk words into a single chunked phrase
    candidates = [' '.join(word for word, pos, chunk in group).lower()
                  for key, group in itertools.groupby(all_chunks, lambda group : group[2] != 'O') if key]
    final_candidates = [cand for cand in candidates
                        if cand not in stop_words and not all(char in punct for char in cand)]
    return final_candidates

def extract_candidate_words(text, good_tags=set(['JJ','JJR','JJS','NN','NNP','NNS','NNPS'])):

    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenize and POS-tag words
    tagged_words = itertools.chain.from_iterable(nltk.pos_tag_sents(nltk.word_tokenize(sent)
                                                                    for sent in nltk.sent_tokenize(text)))
    # filter on certain POS tags and lowercase all words
    candidates = [word.lower() for word, tag in tagged_words
                  if tag in good_tags and word.lower() not in stop_words
                  and not all(char in punct for char in word)]

    return candidates

def score_keyphrases_by_tfidf(texts, candidates='chunks'):
    
    # extract candidates from each text in texts, either chunks or words
    if candidates == 'chunks':
        boc_texts = [extract_candidate_chunks(text) for text in texts]
    elif candidates == 'words':
        boc_texts = [extract_candidate_words(text) for text in texts]
    
    # make gensim dictionary and corpus
    # create dictionary (index of each element)
    dictionary = gensim.corpora.Dictionary(boc_texts)
    dictionary.save('/Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/TEST_DICT.dict')
    #print(dictionary)
    #print(dictionary.token2id)
    
    # compile corpus (vectors number of times each elements appears)
    corpus = [dictionary.doc2bow(boc_text) for boc_text in boc_texts]
    #print(corpus[0:50])
    
    # transform corpus with tf*idf model
    tfidf = gensim.models.TfidfModel(corpus) #initialize a model
    
    corpus_tfidf = tfidf[corpus]
    
    return corpus_tfidf, dictionary
##############################################################
#Directions : http://bdewilde.github.io/blog/2014/09/23/intro-to-automatic-keyphrase-extraction/

direct = '/Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/TEST_EXAMPLE_cr1601.csv'
data = list(csv.DictReader(open(direct, encoding = 'utf-8')))

rawTitles = []

for row in data:
    title = row['Headings'] + '.'
    sub = title.replace('[','').replace(']','').replace("'",'')
    rawTitles.append(sub)

stringing = ' '.join(rawTitles)

final_candidates = list(set(extract_candidate_chunks(stringing)))
print('First 20 candidate keyword chunks: {}'.format(final_candidates[0:20]))

final_candidates = list(set(extract_candidate_words(stringing)))
print('First 20 candidate keywords: {}'.format(final_candidates[0:20]))

text = stringing
result = score_keyphrases_by_textrank(text)
print('Keyphrases and scores with TextRank algorithm: {}'.format(result[0:50]))

'''future_improvements: Normalization of candidates (keyphrase / keyphrases, …) could help, as could better cleaning and filtering. Furthermore, experimenting with different aspects of the algorithm — like DivRank, SingleRank, ExpandRank, CollabRank, and others — including co-occurrence window size, weighted graphs,and the manner in which keywords are merged into keyphrases, has been shown to produce better results.'''

corpus_tfidf, dictionary = score_keyphrases_by_tfidf(text)
#print('NEEDS MAPPING! Corpus of <<term-frequency inverse document frequency>>: {}'.format(corpus_tfidf['']))
   
