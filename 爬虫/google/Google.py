# -*- coding: utf-8 -*-
# @Time    : 2018/12/08 10:24
import requests
from bs4 import BeautifulSoup
import pymongo
import time
import hashlib
import multiprocessing
import random
import re
from Yahoo import log


log_google = log.Log("google_links")
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['Words']
coll = db['keywords_en']
coll_arti = db['Google']
# suoying=client["Words"]["Google"]
# suoying.ensure_index("url_md5",unique=True)

U_A=["Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.6 (KHTML, like Gecko) Chrome/7.0.500.0 Safari/534.6","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
     "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.8 (KHTML, like Gecko) Chrome/7.0.521.0 Safari/534.8",
     "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.540.0 Safari/534.10","Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.540.0 Safari/534.10"]

headers = {
    'User-Agent': random.choices(U_A)[0],
}

def insert_data( href, title, summary, keyword, type):
    url_md5 = get_md5(href)
    data_dict = {'url': href, 'url_md5': url_md5, 'status': 0, 'title': title, 'summary': summary,
                 'keyword': keyword, 'type': type}
    try:
        coll_arti.insert(data_dict)
    except Exception as e:
        pass


def get_ip():
    ip_req = requests.get("http://mp.pachongdaili.com/api.php?order=d1548166098")
    ip_text = ip_req.text
    ip = re.findall(r'\d+.\d+.\d+.\d+', ip_text, re.S)[0]
    ip_proxies = {'http': 'http://dtip123456:dtip123456@' + str(ip) + ':888',
                  'https': 'http://dtip123456:dtip123456@' + str(ip) + ':888'}
    return ip_proxies

def get_md5(url):
    m = hashlib.md5()
    m.update(url.encode("UTF-8"))
    md5 = m.hexdigest()
    return md5


def main():
    count = 0
    while True:
        item = coll.find_one_and_update({'status': 0}, {'$set': {'status': 1}})
        if not item:
            print('已没有关键字可取了！！！')
            break
        keyword = item['_id']
        # keyword="计算机"
        types = ['doc', 'pdf', 'ppt']
        for type in types:
            n = 0
            while True:
                # time.sleep(0)
                success = 0
                duplicate = 0
                payload = {
                    "q": "filetype:" + str(type) + " %s" % keyword,
                    "start": n
                }
                try:
                    proxies = get_ip()
                    print(time.ctime(), proxies)
                    #     proxies = {"http": 'http://te0116w:te0116w@45.125.33.86:888',
                    #                "https": "http://te0116w:te0116w@45.125.33.86:888"}
                    start = time.time()
                    res = requests.get("https://www.google.com.hk/search?num=100&biw=1078&bih=806&ei=QFk9XI24GoTO8wWczY-gCA",headers=headers, params=payload, proxies=proxies, timeout=5)
                    print(time.time() - start)
                    if res.status_code != 200:
                        count += 1
                        print("出错")
                        break
                    else:
                        count = 0
                        print("+" * 50)
                        soup = BeautifulSoup(res.text, "lxml")
                        div_list = soup.select("div.rc")
                        for div in div_list:
                            href = div.select("a")[0].get("href")
                            title = div.select("a > h3 ")[0].get_text()
                            summary = div.select("div.s")[0].get_text()
                            try:
                                insert_data(href, title, summary, keyword, type)
                                success += 1
                            except:
                                duplicate += 1
                        print("插入成功：%s条,重复：%s条" % (success, duplicate))
                        if int(success) <= int(20):
                            # log_google.info("此关键词：%s爬取数量过少,数量：%s"%(keyword,m))
                            print("爬取量过少，可能需要换关键词")
                        if len(soup.select("a.pn")) == 1:
                            if soup.select("a.pn ")[0].get_text() == "Next":
                                n += 100
                            else:
                                print("没有下一页")
                                break
                        else:
                            if soup.select("a.pn")[1].get_text() == "Next":
                                n += 100
                            else:
                                print("没有下一页")
                                break
                except Exception as e:
                    print("出错了,请检查")
                    log_google.error("error delete_mongo: %s" % (e))
                    break
        if count >= 3000:
            break
if __name__ == '__main__':
    trader = []
    for i in range(4):
        pr = multiprocessing.Process(target=main,)
        pr.start()
        trader.append(pr)
    for i in trader:
        i.join()


