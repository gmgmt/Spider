# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 10:12
import requests
from urllib.parse import urlencode
import re
from bs4 import BeautifulSoup
import pymongo
from multiprocessing.pool import Pool

def get_one_page(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'Cookie': 'BAIDUID=B194A3152FF89A5648C8C85F97AFFDB7:FG=1; BIDUPSID=B194A3152FF89A5648C8C85F97AFFDB7; PSTM=1543812881; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; _click_param_pc_rec_doc_2017_testid=4; BDUSS=JYQzlHWUlsdUozTUdUcnJ-UXFvcW90UHlNfm9mM0UzVXF4OUt1M1pPQ010aTFjQVFBQUFBJCQAAAAAAAAAAAEAAACFYoqQa3Jpc2x14pkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwpBlyMKQZcTk; Hm_lvt_e732897225a3e56c38dbe57ca83d52a2=1543971641; locale=zh; Hm_lvt_d8bfb560f8d03bbefc9bdecafc4a4bf6=1543974583,1543975631,1543977239,1543991563; BDRCVFR[RS2Lo0QPSlY]=Msysc7Nbec6rjPEUi4WUvY; H_PS_PSSID=; delPer=0; PSINO=3; Hm_lpvt_d8bfb560f8d03bbefc9bdecafc4a4bf6=1543991777; isJiaoyuVip=1; userFirstTime=true'
        #   加cookies的原因是爬取到后面的时候javascript被禁用了
    }
    try:
        r = requests.get(url, headers=header, timeout=10)
        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            return r.text
        return None
    except:
        print('获取网页失败')
        return None

#   判断总页数的问题
# def get_page_num(html):
#     html = get_one_page(url)
#     pattern3 = re.compile(r'<span class="nums">(.*?)</span>', re.S)
#     result3 = re.findall(pattern3, html)
#     las = result3[0][7:-1]
#     return las
#     # print(result3[0][7:-1])
#     #  print(type(result3))



def parse_html(html):
    pattern = re.compile(r'</span>\n<a href="https://wenku.baidu.com/view/(.*?)search.*?".*?data-flag =', re.S)
    # 所有标题链接, 为一个列表
    result = re.findall(pattern, html)
    # print(result)
    global lst
    lst = []
    for i in result:
        url2 = 'https://wenku.baidu.com/view/' + str(i) + 'search'
        lst.append(url2)
    print(lst)
    soup = BeautifulSoup(html, 'html.parser')
    # span = soup.find_all("span")
    # return span
    div = soup.select("div.detail-info")
    # return div[4:]
    pattern2 = re.compile(r'<div class="detail-info">\n(.*?)\n<i>.*?</i>(.*?)<i>.*?</i>(.*?)<i>.*?</i>\n(.*?)<i>.*?</div>.*?', re.S)
    result2 = re.findall(pattern2, html)
    lst2 = []
    for i in list(result2):
        coupon = list(i)
        # print(type(coupon))
        if coupon[-1][-1] != '券':
            coupon[-1] = '无'
        # print(tuple(coupon))
        lst2.append(tuple(coupon))
        # print(lst2)

    # pattern3 = re.compile(r'<span class="nums">(.*?)</span>', re.S)
    # result3 = re.findall(pattern3, html)
    # global last
    # last = result3[0][7:-1]
    # print(last)
    # print(result3[0][7:-1])
    #  print(type(result3))
    return lst2


def save_to_mongo(result4):
    client = pymongo.MongoClient('192.168.2.214', connect=False)
    db = client['day2']
    #  加个判断, 如果插入数据失败,再次循环
    if db['day2_tb'].insert(result4):
        print("insert into mongo success", result4)
        # 查询当前存储的数据条数
        print('当前已存储%d条数据' % db.day2_tb.find().count())
        return True
    else:
        return False

def get_keyword():
    client1 = pymongo.MongoClient("192.168.2.214", 27017)
    db = client1["keyword"]  # 连接表，
    table = db["words"]  # 连接表的某一类
    mylist = []
    # a = table.find_one()
    for x in table.find({}, {"word": 1}):  # 取出表中word数据
        mylist.append(x.get("word"))  # 添加到数列中
    return mylist

#   下载详情页的文档
# def get_download_url():
#     client1 = pymongo.MongoClient("192.168.2.214", 27017)
#     db = client1["day2"]
#     table = db["day2_tb"]
#     mylist2 = []
#     url = table.find_one()
#     for x in table.find({}, {"url": 1}):  # 取出表中word数据
#         mylist2.append(x.get("url"))  # 添加到数列中
#     return mylist2
def main(keyword, offset):
    n = 0
    keyword = get_keyword()
    # print(keyword)
    params = {
        'word': keyword[n],
        'pn': offset
    }
    url = 'https://wenku.baidu.com/search?' + urlencode(params)
    # print(url)
    html = get_one_page(url)
    # parse_html(html)
    # print(html)
    for item in parse_html(html):
        result4 = {
            "url": lst[n],
            "data": item[0],
            "page": item[1],
            "count": item[2],
            "coupon": item[3],
            'key': 0
        }
        save_to_mongo(result4)
        # print(lst[n])
        n += 1
    # print(get_download_url())
if __name__ == '__main__':
    for i in range(72, 11000+1):
        main('',i*10)
        j = i + 1
        print('当前已完成%d页'% j)