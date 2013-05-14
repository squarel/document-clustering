import pymongo
import re
import json
import nltk
import math
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
from nltk.tokenize import word_tokenize, wordpunct_tokenize,sent_tokenize
from nltk.corpus import stopwords




client = MongoClient('localhost',27017)
db = client.news
collection = db.it_news
corpus = db.it_corpus

corpus.create_index([("word",DESCENDING)])

porter = nltk.PorterStemmer()

addition_stop_words = ["n't","'s",".",",","``","''","?","*","$","\\","/","+","(",")","[","]","{","}"]
i = 0
for doc in collection.find(timeout=False):
    i = i + 1
    print "doc:" + str(i)
    try:
        title = doc['title'].lower()
        text = doc['text'].lower()
        tags = doc['tags']
    except:
        print "*******none type,skip******"
        continue

    tokenized_words = []
    for t in sent_tokenize(text):
        tokenized_words.extend(word_tokenize(t))
    nostop_words = [w for w in tokenized_words if not w in stopwords.words('english')]
    filtered_words = [w for w in nostop_words if not w in addition_stop_words]

    stemmed_words = [porter.stem(t) for t in filtered_words]
    for word in stemmed_words:
        print word
        find_res = corpus.find({"word":word})
        if find_res.count() != 0:
            print "already in db"
            continue
        regex = "\s" + word + ".*"
        try:
            res = collection.find({"text":re.compile(regex, re.IGNORECASE)})
        except:
            continue
        #word_hash_corpus[word] = res.count()
        record = {}
        record['word'] = word
        record['count'] = res.count()
        corpus.insert(record)
        print "insert to db"
