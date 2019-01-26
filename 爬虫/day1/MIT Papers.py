# -*- coding: utf-8 -*-
# @Time    : 2018/11/12 8:00
import requests
import re
import pymongo
import hashlib
from multiprocessing.pool import Pool

def get_one_page(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=header)
        if r.status_code == 200:
            return r.text
        return None
    except:
        print('获取网页失败')
        return None

def get_content(html):
    pattern = re.compile(r'<a href="/handle/1721.1/(.*?)">(.*?)</a>', re.S)
    result = re.findall(pattern, html)
    content = result[1:21]
    for i in content:
        yield{
            'title': i[1],
            'url': 'http://dspace.mit.edu/handle/1721.1/' + i[0]
        }

def get_detail_page(detailurl):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    try:
        r = requests.get(detailurl, headers=header)
        if r.status_code == 200:
            return r.text
        return None
    except:
        print('获取网页失败')
        return None

def save_pdf(pdf):
    pattern = re.compile(r'<a href="/openaccess-disseminate/1721.1/(.*?)">', re.S)
    result = re.findall(pattern, pdf)
    url = 'http://dspace.mit.edu/handle/1721.1/' + result[0]
    return url


def save_to_mongo(result):
    client = pymongo.MongoClient('192.168.2.214', connect=False)
    db = client['test']
    #  加个判断, 如果插入数据失败,再次循环
    if db['table'].insert(result):
        print("insert into mongo success", result)
        # 查询当前存储的数据条数
        print('当前已存储%d条数据'% db.table.find().count())
        return True
    else:
        return False


def md5Encode(url):
    #  创建md5对象
    m = hashlib.md5()
    #  传入需要加密的字符串
    m.update(url.encode("utf8"))
    #  返回加密之后的字符串
    return m.hexdigest()

def main(offset):

    url = 'http://dspace.mit.edu/handle/1721.1/49433/browse?offset=' + str(offset) + '&type=dateissued'
    html = get_one_page(url)
    for item in get_content(html):
        detailurl = item.get('url')
        title = item.get('title')
        # print(detailurl, title)
        pdf = get_detail_page(detailurl)
        # print(pdf)
        url = save_pdf(pdf)
        md5 = md5Encode(url)
        result = {
            "title": title,
            "url": url,
            "md5": md5
        }
        save_to_mongo(result=result)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(1126, 1526 + 1)])
    pool.map(main, groups)
    # 关闭pool，使其不在接受新的（主进程）任务
    pool.close()
    # 主进程阻塞后，让子进程继续运行完成，子进程运行完后，再把主进程全部关掉。
    pool.join()


