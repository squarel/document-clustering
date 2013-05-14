import pymongo
import re
import json
import nltk
import math
import numpy
import random
from pymongo import MongoClient
from nltk.tokenize import word_tokenize, wordpunct_tokenize,sent_tokenize
from nltk.corpus import stopwords
from feature_extraction import find_corpus, compute_idf, preprocess

client = MongoClient('localhost',27017)
db = client.news
collection = db.it_news
corpus = db.it_corpus

#tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
#nltk.download()

def initialize():
    doc_id = {}
    all_docs = []

    #doc_security = collection.find({"tags":re.compile("security", re.IGNORECASE)},timeout=False)
    doc_virtual = collection.find({"tags":re.compile("virtualization", re.IGNORECASE)},timeout=False)
    #doc_tele = collection.find({"tags":re.compile("telecommunication", re.IGNORECASE)},timeout=False)
    doc_electron = collection.find({"tags":re.compile("consumer-electronics", re.IGNORECASE)},timeout=False)
    #doc_hardware = collection.find({"tags":re.compile("hardware-systems-0", re.IGNORECASE)},timeout=False)
    #doc_internet = collection.find({"tags":re.compile("internet", re.IGNORECASE)},timeout=False)
    doc_legal = collection.find({"tags":re.compile("legal", re.IGNORECASE)},timeout=False)
    all_docs.extend(doc_legal[:400])
    #doc_gov = collection.find({"tags":re.compile("government", re.IGNORECASE)},timeout=False)
    #all_docs.extend(doc_gov[:400])
    #doc_business = collection.find({"tags":re.compile("business-issues", re.IGNORECASE)},timeout=False)
    #all_docs.extend(doc_business[:400])

    all_docs.extend(doc_electron[:400])
    ##all_docs.extend(doc_security[:400])
    all_docs.extend(doc_virtual[:400])
    #all_docs.extend(doc_tele[:400])
    #all_docs.extend(doc_hardware[:400])
    #all_docs.extend(doc_internet[:400])
    ##doc_cloud = collection.find({"tags":re.compile("cloud-computing", re.IGNORECASE)},timeout=False)
    ##all_docs.extend(doc_cloud[:400])
    ##doc_storage = collection.find({"tags":re.compile("storage", re.IGNORECASE)},timeout=False)
    ##all_docs.extend(doc_storage[:400])
    ##doc_mobile = collection.find({"tags":re.compile("mobile", re.IGNORECASE)},timeout=False)
    ##all_docs.extend(doc_mobile[:400])
    ##doc_browsers = collection.find({"tags":re.compile("browsers", re.IGNORECASE)},timeout=False)
    ##all_docs.extend(doc_browsers[:400])

    #all_docs = collection.find(timeout=False)
    for doc in all_docs:
        data_feat = {}
        try:
            title = doc['title'].lower()
            text = doc['text'].lower()
            tags = doc['tags']
            obj_id = doc['_id']
            if len(text) <= 2000:
                continue
        except:
            print "*******none type,skip******"
            continue


        weighted_features,tf_words = preprocess(title, text, tags, obj_id)

        for feat,idf in weighted_features[:70]:
            data_feat[feat] = tf_words[feat]
        if data_feat:
            doc_id[obj_id] = data_feat

    return doc_id

def vector_normalize(v1,v2):
    u = []
    v = []
    for key,value in v1.iteritems():
        u.append(value)
        if key in v2.keys():
            v.append(v2[key])
        else:
            v.append(0)

    for key,value in v2.iteritems():
        if key not in v1.keys():
            u.append(0)
            v.append(value)
    return (u,v)

def cosine_distance(data, cent):
    u,v = vector_normalize(data, cent)
    ret = numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v,v)))
    return 1 - ret

def euclidean_distance(data, cent):
    u,v = vector_normalize(data, cent)
    ret = math.sqrt(numpy.sum(numpy.power(numpy.subtract(u, v), 2)))
    return ret

def jaccard_coefficient(data, cent):
    u,v = vector_normalize(data, cent)
    nom = numpy.dot(u,v)
    ret = nom / (numpy.dot(u, u) + numpy.dot(v,v) - nom)
    return 1 - ret

def pearson_correlation_coefficient(data, cent):
    u,v = vector_normalize(data, cent)
    TFa = numpy.sum(u)
    TFb = numpy.sum(v)
    m = len(u)
    nom = m * numpy.sum(numpy.dot(u, v)) - TFa * TFb
    denom = math.sqrt((m*(numpy.sum(numpy.dot(u, u))) - TFa*TFa) * (m*(numpy.sum(numpy.dot(v, v))) - TFb*TFb))
    ret = nom / denom

    if ret >= 0:
        return 1 - ret
    else:
        return -ret

def min_dist(source_id, centroids):
    min_d = 99
    min_obj = "unclassified"
    for key in centroids:
        sim = cosine_distance(source_id,centroids[key])
        #sim = euclidean_distance(source_id,centroids[key])
        #sim = jaccard_coefficient(source_id,centroids[key])
        #sim = pearson_correlation_coefficient(source_id,centroids[key])
        #print "sim:::::::::::" + str(sim)
        if sim < min_d:
            min_d = sim
            min_obj = key

    return (min_d,min_obj)

#def avg_mean(dataset,centroid,n):
    #avg_centroid = {}
    #for k,v in dataset:
        #if k == centroid:
            #for word,tf in doc_id[k]:
                #if word in avg_centroid:
                    #avg_centroid[word] += tf
                #else:
                    #avg_centroid[word] = 0


#centroids : key = centroid id, value = doc
#def spread_centroid(c_number, centroids):





#docs : docs array, doc = (id dict), dict = key value
#data_set :
#centroids : key = centroid id, value = doc
def iteration(c_number,docs):
    centroids = {}
    centroids_number = {}
    total_number = len(docs)
    rand = random.choice(docs.keys())
    centroids[rand] = docs[rand]
    print "Finding centroids"
    for i in range(1,c_number):
        dist = 0
        while dist < 0.80:
            rand = random.choice(docs.keys())
            for cent in centroids.keys():
                dist = cosine_distance(docs[rand], centroids[cent])
                print "i: " + str(i) + "   " + str(dist)
                if dist < 0.80:
                    break
        centroids[rand] = docs[rand]
    print "Found the centroids"
    print docs[rand]
    print centroids[rand]
    print centroids
    dataset = {}

    dist = 99
    loop = True
    #for i in range(1,6):
    while loop:
        previous = centroids_number.copy()
        for k in centroids:
            centroids_number[k] = 0

        for k in docs:
            dist,centroid = min_dist(docs[k],centroids)
            dataset[k] = centroid
            if centroid in centroids_number:
                centroids_number[centroid] += 1
        print centroids_number


    #compute the average of each centroids
        for k,v in dataset.iteritems():
            centroids[v] = {}
            for word,tf in docs[k].iteritems():
                if word in centroids[v].keys():
                    centroids[v][word] += tf
                else:
                    centroids[v][word] = tf

        for k in centroids:
            if centroids_number[k] != 0:
                for word,tf in centroids[k].iteritems():
                    centroids[k][word] = tf / centroids_number[k]


        #loop = False
        #for k in centroids_number.keys():
            #if centroids_number[k] != previous[k]:
                #loop = True
        shared_item = set(centroids_number.items()) & set(previous.items())
        if len(shared_item) == len(centroids_number):
            loop = False
        else:
            loop = True

    return (dataset,centroids)





if __name__ == "__main__":

    #a = {'a':1,'b':2}
    #b = {'c':1,'d':2}
    #c = {'a':2,'b':2}
    #print "------"
    #print cosine_distance(a,b)
    #print cosine_distance(b,c)
    #print cosine_distance(a,c)
    #print "------"
    docs = initialize()
    print "total docs:" + str(len(docs))
    dataset,centroids = iteration(3,docs)

    res = {}
    for doc in docs.iteritems():
        doc_id = doc[0]
        doc_content = collection.find({"_id":doc_id})
        cluster_id = str(dataset[doc_id])
        if cluster_id not in res:
            res[cluster_id] = {}
        #for tag in doc_content[0]['tags']:
        tag = doc_content[0]['tags'][0]
        if tag not in res[cluster_id]:
            res[cluster_id][tag] = 1
        else:
            res[cluster_id][tag] += 1


    for k,v in res.iteritems():
        print "-------------------"
        print "cluster " + str(k)
        for tag,number in v.iteritems():
            print "tag:" + str(tag) + " = " + str(number)



        #print str(dataset[doc_id])
        #print doc_content[0]['tags']


