from bs4 import BeautifulSoup
import os, re, csv, sys
import collections
import json


def get_list_files(filedir2):
    #Uncomment the for loop below to get the list of all html files + comment out next line
    Files = ['-doc-cr1762.html','-doc-cr1753.html']
    #Files = list()
    #for filename in os.listdir(filedir2):
        #if filename.endswith('.html'):
            #Files.append(filename)
    return Files

#Find starting position of whole text and truncate
def id_start(list1,string1):
    last_elm = '(?=' + list1[-1] + ')'
    pattern1 = re.compile(r'{}'.format(last_elm), flags = re.I)
    result = pattern1.search(string1)
    print(result)
    ind = result.start() + len(list1[-1])
    string2 = string1[ind:]
    return string2

def most_common_compilation(mcom):
    comp = []
    for x1,x2 in mcom:
        if x2 > 1:
            comp.append(x1)
        else:
            continue
    comp3 = [r'^' + re.escape(c) + r'$' for c in comp]
    cReg = re.compile('|'.join(comp3))  
    return cReg

#Check if element is an anchor i.e. the next header or next element from list1
def is_not_anchor(ancr, element):
    #print(len(ancr))
    if len(ancr)>20:
        ancrs = ancr[0:20]
    else:
        ancrs = ancr
    ancReg = re.compile(ancrs, flags = re.I)
    if ancReg.search(element):
        print("STOP HIT: {}".format(element))
        return False
    else:
        #print(repr(a))
        return True

def get_dictionary_anchors(l1):
    dictionary = {}
    i = 0
    while i < len(l1)-1:
        dict1 = {l1[i]: l1[i+1]
                 }
        dictionary.update(dict1)
        i = i + 1
    return dictionary

def get_content_table(name_file):
    list1 = []
    list2 = []
    with open('/Users/dariaulybina/Desktop/georgetown/global-economics/find_extract/contents.json') as data_file:
        data = json.load(data_file)
        listing2 = data[name_file][2]
        for l in listing2:
            elm = re.sub(r'\s+',' ',l)
            if len(elm.strip()) < 20:
                list1.append(elm.strip())
                elm2 = '^' + elm.strip()
                list2.append(elm2)
            else:
                list1.append(elm[0:20].strip())
                elm2 = '^' + elm[0:20].strip()
                list2.append(elm2)
    #print(list1)
    return list1, list2

def normalize_spaces(data, list1):
    mainlist = []
    for d in data:
        d2 = re.sub(r'\s+',' ', d)
        mainlist.append(d2)
    main1 = [l for l in mainlist if l] 
    print("Lenth of list: {}".format(len(main1)))
    strT = '|'.join(main1)
    # function id_start locates the poistion of the last element in table of content and cuts out text before that element
    string2 = id_start(list1,strT)
    main3 = string2.split('|')
    main = [x for x in main3 if x != ' ']
    return main

def eliminate_redundancy(main):
        c = collections.Counter(main)
        mcom = c.most_common(100)
        print("Most common elements: {}".format(mcom))
        compReg = most_common_compilation(mcom)
        newlist = []
        numReg = re.compile(r"^[\d\.\,\/\;\:\-\%\$\']{1,}$", re.DOTALL)
        for elm in main:
            if compReg.match(elm) or numReg.match(elm.strip()):
                continue
            else:
                newlist.append(elm)
        print("Length of new list: {}".format(len(newlist)))
        return newlist

def get_chunks(newlist, dictionary, headReg):
    i = 0
    good_list = []
    while i < len(newlist):
        if len(newlist[i])>20:
            chn = newlist[i].strip()[0:20]
        else:
            chn = newlist[i].strip()
        #print(repr("ELEMENT: {}".format(chn)))
        if headReg.match(chn):
            print("got match: {}".format(newlist[i]))
            mydict = {
                'head': newlist[i].strip(),
                'tail': []
                }
            try:
                ancr = dictionary[chn.strip()]
                #print("identified anchor: {}".format(ancr))
            except KeyError:
                #print(repr(chn.strip()))
                print("stop")
                break
            x = 1
            while is_not_anchor(ancr, newlist[i+x].strip()):
                mydict['tail'].append(newlist[i+x].strip())
                #print("Add to tail: {}".format(newlist[i+x]))
                x = x + 1
            good_list.append(mydict)
            i = i + 1
        else:
            i = i + 1
    #make the list of chunks a string of text
    for g in good_list:
        newg = ' '.join(g['tail'])
        g.update({'tail':newg})
    return good_list

#################################################

#change this to folder location where your html files are stored
filedir2 = '/Users/dariaulybina/Desktop/georgetown/global-economics/find_extract/'

FinalList = []

# function should look into your directory and get the list of all html files in it
files_list = get_list_files(filedir2)

for f in files_list:
    name_file = f.replace('.html','')
    print("Reading file : {}".format(f))

    # Get the content table for document from json file
    list1, list2 = get_content_table(name_file)

    # Read html and grab all tags that have text
    soup = BeautifulSoup(open(os.path.join(filedir2, f), encoding = 'utf-8'), 'html.parser')

    #data is an iterable object where text of each tag is an element
    data = soup.find_all(text=True)

    # To see how it looks with different empty spaces, uncomment lines below:
    #for d in data:
        #print(repr(d))

    #normalize_spaces function eliminates all types of spaces (\t,\n,\r,\n\n\n\t...) + replaces them with standard 1-element space
    main = normalize_spaces(data, list1)

    # eliminate_redundancy function identifies most common elements from the list and eliminate evrth that has frequency > 2 
    # For example, 'INTERNATIONAL MONETARY FUND' occuring on every page as a footer/header will be eliminated. 
    # Also eliminates symbols, parts of tables, figures, charts etc
    newlist = eliminate_redundancy(main)

    # headReg - regex pattern that matches one of the elements from table of content list (headers)
    headReg =  re.compile(r'|'.join(list2), re.DOTALL)
    #print(headReg)
    
    # get_dictionary_anchors creates dictionary - each header (except for the last one) is a key with value of the next element
    # Example: {'Intrpdoction': 'Topic 1', 'Topic 1': 'Topic 2', 'Topic 2': 'Conclusion'}
    dictionary = get_dictionary_anchors(list1)
    #print(repr(dictionary))

    # get_chunks iterates over the list of 'lines' (obtained from BeautifulSoup, cleaned and normalized)
    # When the element of content table (header) is matched, a dictionary with 'head','tail' is created, 'tail' = empty list
    # After the header match, every following element gets appended to 'tail', creating the body of text chunk
    # When the anchor (next header element) matches with a line - appending stops and returns dictionary
    # Function returns 1 list of dictionaries for a document with key-value pairs: 'head': element of content table,
    # 'tail': everything between the element of content table and next the following element of the content table
    good_list = get_chunks(newlist, dictionary, headReg)

    # create dictionary with content and document id and append the output to final list
    dict2 = {
        'doc': name_file,
        'content': good_list
        }
    FinalList.append(dict2)

# save the final list of ids and contents to json
with open('/Users/dariaulybina/Desktop/georgetown/global-economics/find_extract/file_out.json', 'w') as outfile:
    json.dump(FinalList, outfile, sort_keys=True,  indent = 4)
