# -*- coding: utf-8 -*-
# @Time    : 2018/8/1 11:11
import os

path = os.path.abspath(os.path.dirname(os.getcwd()))
import sys

sys.path.append(path)
import pymongo

# 线上mongo
MONGODB_URI = 'mongodb://192.168.8.130:27017'
# MONGODB_NAME = "doc"
# WORDS_NAME = 'Sougou_pdf_url_new'

db = pymongo.MongoClient(MONGODB_URI)
sougou_url = db['sougou']['sougou_new_links']

MONGODB_URI_two = 'mongodb://192.168.8.211:27017'
db_two = pymongo.MongoClient(MONGODB_URI_two)
con_proxy = db_two['proxy']
con_proxy_dongtai = db_two['proxy']['proxies_ip_dongtai']
li_db_words = db_two['springer_meta_20180809']['keywords_cn']
li_db_words_en = db_two['springer_meta_20180809']['keywords_en']
