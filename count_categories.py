import pymongo
from pymongo import MongoClient

client = MongoClient('localhost',27017)
db = client.news
collection = db.it_news



if __name__ == "__main__":
    all_docs = collection.find(timeout=False)

    first_tag = {}
    all_tag = {}

    count = 0
    for doc in all_docs:
        count += 1
        try:
            tags = doc['tags']
            obj_id = doc['_id']
        except:
            print "*******none type,skip******"
            continue
        print count
        print "tags:" + tags[0] + "-" +  tags[1]

        if tags[0] in first_tag:
            first_tag[tags[0]] += 1
            all_tag[tags[0]] += 1
        else:
            first_tag[tags[0]] = 1
            all_tag[tags[0]] = 1

        if tags[1] in all_tag:
            all_tag[tags[1]] += 1
        else:
            all_tag[tags[1]] = 1

    print "-------------------"
    print "main tag:"
    print "count:" + str(len(first_tag.keys()))
    for k,v in first_tag.items():
        if v >= 300:
            print k + ":" + str(v)
    print "-------------------"
    print "all tag:"
    print "count:" + str(len(all_tag.keys()))
    for k,v in all_tag.items():
        if v >= 300:
            print k + ":" + str(v)


