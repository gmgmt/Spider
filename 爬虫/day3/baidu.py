# -*- coding: utf-8 -*-
# @Time    : 2018/11/20 14:20

import pymongo
import requests
from urllib.parse import urlencode
from lxml import etree
import hashlib
from multiprocessing.pool import Pool
from requests import codes
from bs4 import BeautifulSoup

client1 = pymongo.MongoClient("192.168.8.211", 27017)
db = client1["day4"]  # 连接表，
table = db["keywords_new"]  # 连接表的某一类
def get_page():
    while 1:
        data = table.find_and_modify({"state": 1}, {"$set": {"state": 0}})  # 替换MongoDB中的第一个匹配的数据
        # 此函数匹配第一个参数，若存在，则用第二个替换，若无匹配则反回None
        if not data:
            # 如果替换则表示已下载，not None为True,跳出循环
            return
        keyword1 = data["keyword"]
        keyword = 'filetype:pdf ' + keyword1 + ' -(site:wenku.baidu.com)'
        # print('当前关键词为{}'.format(keyword))
        # print(keyword)
        print('当前已搜索%d条数据' % db.keywords_new.find({'state': 0}).count())
        params = {
            # 'wd': keyword,
            'wd': 'filetype:pdf 内共生 -(site:wenku.baidu.com)',
            'pn': '0'
        }
        base_url = 'https://www.baidu.com/s?'
        url = base_url + urlencode(params)
        # print(url)
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }
        n= 1
        while 1:
            try:
                r = requests.get(url, headers=header)
                # print(url)
                if codes.ok == r.status_code:
                    html = r.text
            except requests.ConnectionError:
                table.update({"keyword": keyword}, {"$set": {"keyword": -1}})
                continue
            content = etree.HTML(html)

            try:
                #  r 为单页所有pdf链接
                pdfs = content.xpath('//h3/font/following-sibling::a/@href')
                titles = content.xpath('//div[@class="c-tools"]/@data-tools')
                for i in range(len(titles)):
                    a = str(titles[i])
                    title = a.split(',')[0][10:-1]
                soup = BeautifulSoup(html, 'lxml')
                a = soup.find_all('div', "c-abstract")
                for b in a:
                    summary= b.get_text().split("\n")[0]
                # summarys = content.xpath('//div[contains(@class, "c-abstract")]')
                next_page = content.xpath('//a[contains(text(),"下一页>")]/@href')
                # if len(r) == 0:
                #     print("无内容")
                #     table.update({"word": keyword}, {"$set": {"key": -1}})
                #     continue
                for pdf in pdfs:
                    # print(pdf)
                    url_1 = requests.get(pdf).url
                    md5 = md5Encode(url_1)
                    result = {
                        'url': url_1,
                        'title': title,
                        'summary': summary,
                        'state': 0,
                        'url_md5': md5,
                        'type': 'pdf',
                        'q': keyword
                    }
                    save_to_mongo(result)
                n += 1
                if len(next_page) != 0:
                    print("第{}页开始：".format(n))
                    url = "https://www.baidu.com" + next_page[0]
                    continue
                else:
                    break
            except:
                print('111')
                pass



def save_to_mongo(result):
    client = pymongo.MongoClient('192.168.8.211', connect=False)
    db = client['day4']
    try:
        #  加个判断, 如果插入数据失败,再次循环
        if db['day4_tb'].insert(result):
            print("insert into mongo success", result)
            # 查询当前存储的数据条数
            print('当前已存储%d条数据' % db.day4_tb.find().count())
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
    get_page()

if __name__ == '__main__':

    pool = Pool(10)
    for i in range(20):
        pool.apply_async(get_page)
    pool.close()
    pool.join()

