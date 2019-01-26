# -*- coding: utf-8 -*-
# @Time    : 2018/12/08 10:00
import requests
import pymongo
from lxml import etree
from multiprocessing.pool import Pool

client1 = pymongo.MongoClient('localhost', 27017)
db = client1["shu"]  # 连接表，
table = db["shu_tb"]  # 连接表的某一类
url_2 = 'https://d.qianzhan.com/xdata/list/xfyyy0yyIxPyywyy2xDxfd.html'
table.insert_one(
    {'state': 0, 'pid': 1, 'title': '中国宏观', 'url': url_2,
     'cid': 'null', 'depth': 1})
data = db.shu_tb.find_one()
print(data)
url = data["url"]
# print(url)
n = data["depth"]
m = 2
all_url = []


def get_urls(url, n):
    global m, url_2
    r = requests.get(url)
    html = r.text
    content = etree.HTML(html)
    q = '//div[@class="searchfilter_sub"][' + str(n) + ']//a/@href'
    urls = content.xpath(q)
    urls_1 = urls[1:]
    w = '//div[@class="searchfilter_sub"][' + str(n) + ']//a/text()'
    titles = content.xpath(w)
    if titles[1] == '年度数据':
        return
    else:
        titles_1 = titles[1:]
        data3 = table.find_one({"url": url_2})

        l = data3["pid"]
        if len(titles_1) != 0:
            for (x, y) in zip(urls_1, titles_1):
                url_1 = 'https://d.qianzhan.com' + str(x)
                result = {
                    'pid': m,
                    'title': y,
                    'url': url_1,
                    'cid': l,
                    'depth': n+1,
                    "state": 0
                }
                m += 1
                save_to_mongo(result)
            for i in urls_1:
                # global url_2
                url_2 = 'https://d.qianzhan.com' + str(i)
                get_urls(url_2, n+1)
        else:
            return

def save_to_mongo(result):
    client = pymongo.MongoClient('localhost', connect=False)
    db = client['shu']
    try:
        #  加个判断, 如果插入数据失败,再次循环
        if db['shu_tb'].insert(result):
            print("insert into mongo success", result)
            # 查询当前存储的数据条数
            print('当前已存储%d条数据' % db.shu_tb.find().count())
            return True
        else:
            print('插入失败')
            return False
    except:
        print('url重复')

def main():
    get_urls(url, n)


if __name__ == '__main__':

    # pool = Pool(10)
    # for i in range(20):
    #     pool.apply_async(get_urls)
    # pool.close()
    # pool.join()

    main()