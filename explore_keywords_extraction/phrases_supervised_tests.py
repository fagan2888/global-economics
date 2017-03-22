import collections
import math
import nltk
import sys, csv, os, re

def extract_candidate_features(candidates, doc_text, doc_excerpt, doc_title):
    
    candidate_scores = collections.OrderedDict()
    
    # get word counts for document
    doc_word_counts = collections.Counter(word.lower()
                                          for sent in nltk.sent_tokenize(doc_text)
                                          for word in nltk.word_tokenize(sent))
    
    for candidate in candidates:
        
        pattern = re.compile(r'\b'+re.escape(candidate)+r'(\b|[,;.!?]|\s)', re.IGNORECASE)
        
        # frequency-based
        # number of times candidate appears in document
        cand_doc_count = len(pattern.findall(doc_text))
        # count could be 0 for multiple reasons; shit happens in a simplified example
        if not cand_doc_count:
            print('**WARNING: {} not found'.format(candidate))
            continue
    
        # statistical
        candidate_words = candidate.split()
        max_word_length = max(len(w) for w in candidate_words)
        term_length = len(candidate_words)
        # get frequencies for term and constituent words
        sum_doc_word_counts = float(sum(doc_word_counts[w] for w in candidate_words))
        try:
            # lexical cohesion doesn't make sense for 1-word terms
            if term_length == 1:
                lexical_cohesion = 0.0
            else:
                lexical_cohesion = term_length * (1 + math.log(cand_doc_count, 10)) * cand_doc_count / sum_doc_word_counts
        except (ValueError, ZeroDivisionError) as e:
            lexical_cohesion = 0.0
        
        # positional
        # found in title, key excerpt
        in_title = 1 if pattern.search(doc_title) else 0
        in_excerpt = 1 if pattern.search(doc_excerpt) else 0
        # first/last position, difference between them (spread)
        doc_text_length = float(len(doc_text))
        first_match = pattern.search(doc_text)
        abs_first_occurrence = first_match.start() / doc_text_length
        if cand_doc_count == 1:
            spread = 0.0
            abs_last_occurrence = abs_first_occurrence
        else:
            for last_match in pattern.finditer(doc_text):
                pass
            abs_last_occurrence = last_match.start() / doc_text_length
            spread = abs_last_occurrence - abs_first_occurrence

        candidate_scores[candidate] = {'term_count': cand_doc_count,
                                       'term_length': term_length, 'max_word_length': max_word_length,
                                       'spread': spread, 'lexical_cohesion': lexical_cohesion,
                                       'in_excerpt': in_excerpt, 'in_title': in_title,
                                       'abs_first_occurrence': abs_first_occurrence,
                                       'abs_last_occurrence': abs_last_occurrence}
        print('Candidate score <<{}>>: {}'.format(candidate, candidate_scores[candidate]))
    return candidate_scores
#########################################################

direct = 'Users/dariaulybina/Desktop/georgetown/global-economics/explore_keywords_extraction/TEST_EXAMPLE_cr1601.csv'
data = list(csv.DictReader(open(direct, encoding = 'utf-8')))

rawTitles = []

for row in data:
    title = row['Headings'] + '.'
    sub = title.replace('[','').replace(']','').replace("'",'')
    rawTitles.append(sub)


stringing = ' '.join(rawTitles)
#text = stringing
#result = score_keyphrases_by_textrank(text)
#print(result[0:20])

#Terms below are just random examples chosen - please feel free to adjust for any keyterms you derive in your testing
candidates = ['fiscal policy','monetary policy','deficit','economic vulnerabilities','subsidies',
              'tax revenue', 'budget deficit','fiscal liabilities',' energy sector','arrears','debt']

doc_text = ' '.join(rawTitles) #you can change this to full text or to section you want to look at
doc_excerpt = ' '.join(rawTitles) #could be a summary? 
doc_title = 'Pakistan : Staff Report for the 2015 Article IV Consultation, Ninth Review Under the Extended Arrangement, Request for Waivers of Nonobservance of Performance Criteria, and Request for Modification of a Performance Criterion-Press Release; Staff Report;and Statement by the Executive Director for Pakistan'
extract_candidate_features(candidates, doc_text, doc_excerpt, doc_title)

