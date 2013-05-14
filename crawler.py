import requests
import re
import time
import pymongo
from goose.Goose import Goose
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost',27017)
db = client.news
collection = db.it_news

crawl_list = ['business-issues','consumer-electronics','telecommunication','internet','networking','peripherals','security','services','software','storage','virtualization','hardware-systems-0','government','business-issues','cousumer-electronics','legal','it-management']
page_max = 400
item_per_page = 10

go = Goose()
url_base = 'http://www.itnews.com/'
for tag1 in crawl_list:
    print "TAG:::::::" + tag1
    for page in range(0,page_max):
        new_articles = []

        if page == 0:
            url_page = ''
        else:
            url_page = '?page=' + str(page)

        url_full = url_base + tag1 + url_page
        print "URL::::::" + url_full
        time.sleep(1)
        res = requests.get(url_full)
        print "PAGE:::::" + str(page)
        soup = BeautifulSoup(res.content)

        #check if have "next" in page
        last_page = len(soup.find_all("li","pager-next"))
        for row in soup.find_all("div","views-row"):
            new_article = {}
            tags = []
            attr_a = row.find("a")
            url = attr_a['href']
            #extract the tag from url, only the word, not the number
            print "Finding::::" + url
            cats = re.findall(r"/([a-z-]+)/",url)
            if len(cats) == 0:
                print "*****Can't find tag2"
                continue
            tag2 = cats[0]
            url_full = url_base + url
            print url_full
            article = go.extractContent(url=url_full)
            #print article.title
            #print article.cleanedArticleText[:150]
            tags.append(tag1)
            tags.append(tag2)
            print "TAGS:::::" + tag1 + "::" + tag2
            print "-------------------------------"
            new_article['tags'] = tags
            new_article['title'] = article.title
            new_article['text'] = article.cleanedArticleText

            #check if db has that record
            if collection.find({"title":new_article['title']}).count() == 0:
                new_articles.append(new_article)

        if len(new_articles) == 0:
            print "No new title on this page"
        else:
            article_id = collection.insert(new_articles)
            if article_id:
                print "Insert to db!"
            else:
                print "Insert failed"
        if last_page == 0:
            print "To the last page of the category, skip to next"
            break





