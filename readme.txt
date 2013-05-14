Structure:
    crawler.py : crawl various types of news from itnews.com and store them into mongodb
    feature_extraction.py : functions concern the feature extraction
    create_corpus.py: build the corpus manually, it will make kmeans run faster
    kmeans.py: kmeans clustering on three specific categories
    count_categories.py: a script to count categories in the database
    python-goose: the library to extract principle content of a web page

    
Environment:
    Lang: Python2.7.2
    Dependency: numpy, nltk, goose, pymongo, beautifulsoup, requests
    Persistent: mongodb

Corpus and data has more than 300MB, so I just dump 1000 news records into json format. See head1000_news.json

To run the program:
    1.Build the environment, mongodb use localhost
    2.python crawler.py
    3.python kmeans.py(It will run very slow for the first time.After that, it will run much faster due to the results has been
    stored in the database)

All codes are written by me, except the dependencies above.

    
