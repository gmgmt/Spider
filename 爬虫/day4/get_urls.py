
# -*- coding: utf-8 -*-
# @Time    : 2018/11/22 11:08
import pymongo
import requests
from urllib.parse import urlencode
from lxml import etree
import hashlib
from multiprocessing.pool import Pool
from requests import codes
import lxml
import re
from bs4 import BeautifulSoup

def get_html(url):
    try:
        r = requests.get(url)
        if codes.ok == r.status_code:
            return r.text
    except requests.ConnectionError:
        return None

def get_urls(html):
    soup = BeautifulSoup(html, 'lxml')
    a = soup.find_all('form')
    b = a[1].find_all('tr')
    for i in b:
        urls = i.find_all('a')
        url_2 = urls[0]['href']
        url_3 = 'https://ntrs.nasa.gov/' + url_2
        # print(url_3)
        md5 = md5Encode(url_1=url_3)
        result = {
            'md5': md5,
            'url': url_3,
            'state': 0
        }
        save_to_mongo(result)

def save_to_mongo(result):
    client = pymongo.MongoClient('192.168.8.211', connect=False)
    db = client['experiment']

    try:
        #  加个判断, 如果插入数据失败,再次循环
        if db['day9_url'].insert(result):
            print("insert into mongo success", result)
            # 查询当前存储的数据条数
            print('当前已存储%d条数据' % db.day9_url.find().count())
            return True
        else:
            print('插入失败')
            return False
    except:
        print('md5重复')
def md5Encode(url_1):
    #  创建md5对象
    m = hashlib.md5()
    #  传入需要加密的字符串
    m.update(url_1.encode("utf8"))
    #  返回加密之后的字符串
    return m.hexdigest()



def main():
    for i in range(9000,27311):
        page = i * 10
        print(page)
        params = {
            'No=': page
        }
        q = urlencode(params).replace('%3D', '')
        base_url = 'https://ntrs.nasa.gov/search.jsp?N=4294129243&'
        # print(base_url)
        url = base_url + q
        print(url)
        html = get_html(url=url)
        m = get_urls(html)
if __name__ == '__main__':
    # main()
    pool = Pool(10)
    for i in range(20):
        pool.apply_async(main)
    pool.close()
    pool.join()
