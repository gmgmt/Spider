# -*- coding: utf-8 -*-
# @Time    : 2019/1/22 10:18
import os
import sys

path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path)

from sougou import config

sougou_urls = config.sougou_url

db = sougou_urls.find().batch_size(300)
a = 0
for i in db:
    a += 1
    if a % 1000 == 0:
        print(a, i['url_md5'])
    sougou_url = i['url']
    if a>18900000 and sougou_url.find("http") == -1:
        try:
            sougou_urls.delete_one({"url_md5": i['url_md5']})
        except:
            pass
