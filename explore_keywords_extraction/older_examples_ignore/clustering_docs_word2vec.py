"""
    First, Thanks to the gread post by Amir Amini[https://www.kaggle.com/amirhamini/d/benhamner/nips-2015-papers/find-similar-papers-knn] 
    and brandonrose [http://brandonrose.org/clustering]
    
    This script describes a method that using word2vec model.
    step one: extract keywords from Title, Abstract and PaperText based on tf-idf
    step two: keywords are used to build the word2vec model
    step three: from keywords to paper document, average the top-n keywords vector to represent the whole paper
    
    Here are also two clustering method: k-means and Hirerachical clustering.
"""
import pandas as pd
import numpy as np
import nltk
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer('english')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.spatial.distance import squareform,pdist
from wordcloud import WordCloud
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import re
import gensim
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#data = pd.read_csv('/Users/dariaulybina/Desktop/WithKeywords&Titles.csv')
data = pd.read_csv('/Users/dariaulybina/Desktop/georgetown/global-economics/scrape_articles/summary_tables_2000.csv', encoding ='latin1')
"""
    step one:
    extract keywords per paper from Papers Data
    text clean -> tokenize -> stem -> tfidf -> keywords. 
"""
def clean_text(text):
    list_of_cleaning_signs = ['\x0c','\n']
    for sign in list_of_cleaning_signs:
        text = text.replace(sign, ' ')
    clean_text = re.sub('[^a-zA-Z]+',' ',text)
    return clean_text.lower()

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

def top_tfidf_feats(row, terms, top_n=25):
    top_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [terms[i] for i in top_ids]
    return top_feats

def extract_tfidf_keywords(texts, top_n=25):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, max_features=2000000,
                                      min_df=0.05, stop_words="english",
                                      use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    terms = tfidf_vectorizer.get_feature_names()
    arr = []
    for i in range(0, tfidf_matrix.shape[0]):
        row = np.squeeze(tfidf_matrix[i].toarray())
        feats = top_tfidf_feats(row, terms, top_n)
        arr.append(feats)
    return arr

#data['TITLE'] = data['TITLE'].apply(lambda x:clean_text(x))
#data['TOC'] = data['LIST_SUB'].apply(lambda x:clean_text(x))
#data['DOC'] = data['DOC']

data['Summary'] = data['Description'].apply(lambda x:clean_text(x))
data['Subject'] = data['Subject'].apply(lambda x:clean_text(x))
data['Filename'] = data['Filename']

#title2kw = extract_tfidf_keywords(papers_data['Title_clean'],3)
title2kw = extract_tfidf_keywords(data['Subject'], 3)
text2kw = extract_tfidf_keywords(data['Summary'],20) 

"""
    step two:
    word2vec representation
"""
word2vec_model = gensim.models.Word2Vec(title2kw+text2kw, size=100, window=5, min_count=5, workers=4)
print(word2vec_model)
print(word2vec_model.wv.vocab)
word2vec_model.save("/Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/outputs_word2vec/word2vec.model")
#model = Word2Vec.load("/Users/dariaulybina/Desktop/word2vec.model")
#print(word2vec_model['subsidi'])

"""
    step three:
    average top-n keywords vectors and compute similarities
"""
doc2vecs = []
for i in range(0, len(title2kw)):
    vec = [0 for k in range(100)] 
    for j in range(0, len(title2kw[i])):
        if title2kw[i][j] in word2vec_model:
            vec += word2vec_model[title2kw[i][j]]
            
    for j in range(0, len(text2kw[i])):
        if text2kw[i][j] in word2vec_model:
            vec += word2vec_model[text2kw[i][j]]
    doc2vecs.append(vec)

similarities = squareform(pdist(doc2vecs, 'cosine'))

"""
    k-means clustering and wordcloud(it can combine topic-models 
    to give somewhat more interesting visualizations)
"""
num_clusters = 10
km = KMeans(n_clusters=num_clusters)
km.fit(doc2vecs)
clusters = km.labels_.tolist()

#papers = { 'Id': data['DOC'], 'Title': data['TITLE'], 'Date': data['FRONT_DATE (MONTH&YEAR)'],'Country': data['COUNTRY'], 'Cluster': clusters, 'Ttags': data['LEVEL1'], 'Contents': data['TOC']}
#papers_df = pd.DataFrame(papers, index = [clusters] , columns = ['Id', 'Title', 'Date', 'Country','Cluster', 'Ttags', 'Contents'])

papers = { 'Id': data['Filename'], 'Summary': data['Summary'], 'Cluster': clusters, 'Subject': data['Subject']}
papers_df = pd.DataFrame(papers, index = [clusters] , columns = ['Id','Subject', 'Summary','Cluster'])
papers_df['Cluster'].value_counts()

def wordcloud_cluster_byIds(cluId):
    texts = []
    for i in range(0, len(clusters)):
        if clusters[i] == cluId:
            for word in title2kw[i]:
                texts.append(word)
            for word in text2kw[i]:
                texts.append(word)
    
    wordcloud = WordCloud(max_font_size=40, relative_scaling=.8).generate(' '.join(texts))
    plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("/Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/outputs_word2vec"+str(cluId)+".png")

wordcloud_cluster_byIds(2)
wordcloud_cluster_byIds(4)
wordcloud_cluster_byIds(9)