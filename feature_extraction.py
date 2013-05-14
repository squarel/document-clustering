import pymongo
import re
import json
import nltk
import math
from pymongo import MongoClient
from nltk.tokenize import word_tokenize, wordpunct_tokenize,sent_tokenize
from nltk.corpus import stopwords


client = MongoClient('localhost',27017)
db = client.news
collection = db.it_news
corpus = db.it_corpus

def find_corpus(word,collection):
    find_res = corpus.find({"word":word},timeout=False)
    if find_res.count() != 0:
        #print "already in db"
        return find_res[0]['count']
    regex = "\s" + word + ".*"
    try:
        res = collection.find({"text":re.compile(regex, re.IGNORECASE)},timeout=False)
    except:
        return 0
    record = {}
    record['word'] = word
    record['count'] = res.count()
    corpus.insert(record)
    print word + ":insert to db"

    return res.count()

def compute_idf(count,total):
    try:
        idf = math.log(total/(count+1))
        return idf
    except:
        print "*********excpetion*****"
        print "count" + str(count)
        print "total" + str(total)
        print "********exception******"
        return 0

def preprocess(title, text, tags, obj_id):
    porter = nltk.PorterStemmer()
    total = collection.count()
    addition_stop_words = ["n't","'s",".",",","``","''","?","*","$","\\","/","+","(",")","[","]","{","}",":",";"]

    tokenized_words = []
    title = title + " "
    new_text = text + title * 3
    #add weight to title word
    #punctuation = re.compile()
    new_text = re.sub(r'[-.?!,\'%:;()|0-9"]', " ",new_text)
    for t in sent_tokenize(new_text):
        tokenized_words.extend(word_tokenize(t))
    nostop_words = [w for w in tokenized_words if not w in stopwords.words('english')]
    filtered_words = [w for w in nostop_words if not w in addition_stop_words]

    stemmed_words = [porter.stem(t) for t in filtered_words]
    punctuation = re.compile(r'[-.?!,":;()&|0-9"]')
    nopunc_words = [punctuation.sub("", word) for word in stemmed_words]
    #print stemmed_words
    tf_words = nltk.FreqDist(nopunc_words)
    tf_keys = tf_words.keys()
    tf_values = tf_words.values()
    for key in tf_keys:
        #print key
        idf = compute_idf(find_corpus(key,collection),total)
        #print idf
        tf_words[key] = tf_words[key]*idf
        #print tf_words[key]

    weighted_features = sorted(tf_words.items(), key=lambda x: x[1], reverse=True)
    collection.update({'_id':obj_id},{'$set':{'features':json.dumps(weighted_features)}},False)
    #print title
    #print text
    #print weighted_features
    #print tags
    return (weighted_features, tf_words)

if __name__ == "__main__":
    #tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
    #nltk.download()

    docs = collection.find(timeout=False)
    page = 0
    for doc in docs:
        page = page + 1
        print "========page:" + str(page)

        try:
            title = doc['title'].lower()
            text = doc['text'].lower()
            tags = doc['tags']
            obj_id = doc['_id']
        except:
            print "*******none type,skip******"
            continue

        preprocess(title, text, tags, obj_id)

    #docs = collection.find(timeout=False)
    #count = 0
    #page = 0
    #for doc in docs:
        #page += 1
        #print "page:" + str(page)
        #try:
            #title = doc['title'].lower()
            #text = doc['text'].lower()
            #tags = doc['tags']
            #obj_id = doc['_id']
        #except:
            #print "*******none type,skip******"
            #continue

        #if len(text) >= 3000:
            #count += 1
            #print "count" + str(count)
            ##print text





