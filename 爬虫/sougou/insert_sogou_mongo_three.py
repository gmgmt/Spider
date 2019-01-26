# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 11:31
import threading
import os

path = os.path.abspath(os.path.dirname(os.getcwd()))
import sys

sys.path.append(path)
import random, json
import requests, re
from hashlib import md5
from datetime import datetime
from collections import OrderedDict
from multiprocessing import Process, Queue, Pool
from time import sleep
from sougou import config,log
from lxml.html import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36',
}
log_sougou = log.Log("sougou_links")
sougou_url = config.sougou_url
li_db_words = config.li_db_words
con_proxy_dongtai = config.con_proxy_dongtai


class Insertsql(object):
    def __init__(self) -> None:
        self.pro = self.get_pro()
        self.page_num = 0
        self.beifeng = 0

    #   代理
    def get_pro(self):
        db_one = config.con_proxy
        li_db_one = db_one['proxies_ip']
        xx_pro = []
        li_db_two = li_db_one.find()
        for i in li_db_two:
            ip = i['ip']
            xx_pro.append({"http": ip, "https": ip})
        return xx_pro

    #   每页100条的cookies
    def find_cookie(self, proxies=None):
        nuid_num = 0
        while 1:
            if nuid_num > 10:
                new_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_sougou.info("异常结束 %s  %s nuid_num>10" % (new_time, os.getpid()))
                print(new_time)
                print("异常结束 %s  %s nuid_num>10" % (new_time, os.getpid()))
                sys.exit()
            try:
                nuid_num += 1
                ip = con_proxy_dongtai.find()[random.randint(0,25)]['ip']
                proxies = {"http": ip, "https": ip}
                self.ses = requests.session()
                self.ses.get("https://www.sogou.com/", proxies=proxies, headers=headers, timeout=360)
                self.ses.get(
                    "http://www.sogou.com/web?query=filetypedoc+%E7%AE%80%E5%8E%86&ie=utf8&_ast=1547537280&_asf=null&w=01025001&pid=sogou-wsse-af5baf594e9197b4-0001&duppid=1&p=40040108&dp=1&cid=&s_from=result_up&oq=filetype%3Adoc+&ri=0&sourceid=sugg&suguuid=d2abfa7e-4cc8-4dea-a787-5050d4fadbbf&stj=0%3B0%3B0%3B0&stj2=0&stj0=0&stj1=0&hp=0&hp1=&suglabid=suglabId_1&sut=113040&sst0=1547537434703&lkt=12%2C1547537345461%2C1547537370975",
                    proxies=proxies, headers=headers,
                    timeout=360)
                my_cookies = self.ses.cookies.get_dict()
                if my_cookies['SNUID']:
                    my_cookies['com_sohu_websearch_ITEM_PER_PAGE'] = '100'
                    my_cookies['SUV'] = '004D1798AB5332C25C3D8D088CF47553'
                    return my_cookies
            except:
                sleep(1)


    def Method_one(self, proxies=None):
        nuid_num = 0
        while 1:
            try:
                if nuid_num > 8:
                    new_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_sougou.info("异常结束 %s  %s" % (new_time, os.getpid()))
                    print(new_time)
                    sys.exit()
                nuid_num += 1
                url = "http://www.sogou.com/antispider/detect.php?sn=E9DA81B7290B940A0000000058BFAB0&wdqz22=12&4c3kbr=12&ymqk4p=37&qhw71j=42&mfo5i5=7&3rqpqk=14&6p4tvk=27&eiac26=29&iozwml=44&urfya2=38&1bkeul=41&jugazb=31&qihm0q=8&lplrbr=10&wo65sp=11&2pev4x=23&4eyk88=16&q27tij=27&65l75p=40&fb3gwq=27&azt9t4=45&yeyqjo=47&kpyzva=31&haeihs=7&lw0u7o=33&tu49bk=42&f9c5r5=12&gooklm=11&_=1488956271683"
                headers = {"Cookie":
                               "ABTEST=0|1488956269|v17;\
                             IPLOC=CN3301;\
                             SUID=E9DA81B7290B940A0000000058BFAB7D;\
                             PHPSESSID=rfrcqafv5v74hbgpt98ah20vf3;\
                             SUIR=1488956269"
                           }
                ip = con_proxy_dongtai.find()[random.randint(0, 25)]['ip']
                proxies = {"http": ip, "https": ip}
                f = requests.get(url, headers=headers, proxies=proxies).content
                f = json.loads(f)
                Snuid = f["id"]
                if Snuid:
                    print(Snuid)
                    return Snuid
            except Exception as e:
                sleep(1)

    def find_ones(self, data, proxies):
        for x in range(1, 2):
            try:
                data['page'] = str(x)
                req = requests.get('https://www.sogou.com/web?', params=data, cookies=self.my_cookies, headers=headers,
                                   timeout=10)
                req.close()
                if req.status_code != 200:
                    return
                con_et = etree.HTML(req.text)
                result_s = con_et.xpath('//div[@class="rb"]')
                res_len = len(result_s)
                if res_len == 0:
                    self.beifeng += 1
                    if self.beifeng >= 15:
                        new_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        log_sougou.info("异常结束 %s  %s  self.beifeng>15" % (new_time, os.getpid()))
                        # print(new_time)
                        # print("异常结束 %s  %s  self.beifeng>10" % (new_time, os.getpid()))

                    elif str(req.text).find("n=decodeURIComponent") > -1 or self.beifeng % 5 == 0:
                        # print("被封")
                        self.my_cookies = self.find_cookie(proxies)
                        print("获取新的cookies", self.my_cookies['SNUID'], self.page_num, os.getpid())
                        log_sougou.error("获取新的cookies_SNUID : %s  ip : %s  beifeng : %s"%(self.my_cookies['SNUID'], os.getpid(), self.beifeng))
                        self.page_num = 1
                    return
                self.beifeng = 0
                for xiabiao, nr in enumerate(result_s):
                    try:
                        href = nr.xpath('.//h3/a/@href')[1]
                        if (href).find("http") > -1:
                            title_s = nr.xpath('.//h3/a[1]//text()')
                            title = "".join(title_s)
                            content_s = nr.xpath('.//div[@class="ft"]//text()')
                            summary = self.repl("".join(content_s))
                            self.insert_mongo_sougou(href, title, summary, data['query'])
                            if self.page_num % 10 == 0 and xiabiao == (res_len - 1):
                                print("jiansuo_url len(): %s  page: %s  keyword:%s " % (
                                    res_len, str(x), data['query']))
                    except Exception as e:
                        pass
            except Exception as e:
                print(e)
        return

    def insert_mongo_sougou(self, url, title, summary, q):
        url_md5 = self.md5_generator(url)
        save = OrderedDict()
        save['url'] = url
        save['title'] = title
        save['abstract'] = summary
        save['status'] = 0  # 状态
        save['url_md5'] = url_md5
        save['q'] = q
        try:
            sougou_url.insert(save)
        except Exception as e:
            if str(e).find("E11000") > -1:
                return
            print("插入失败：%s" % (e))

    def repl(self, text):
        try:
            new_text = re.sub(r"[\n\t\r\u3000\xa0\u2002]", "", text).strip()
            return new_text
        except:
            return text

    def delete_mongo(self, proxies, num):
        new_time = datetime.now()
        log_sougou.info("开始 %s  %s" % (new_time.strftime('%Y-%m-%d %H:%M:%S'), os.getpid()))
        print(new_time.strftime('%Y-%m-%d %H:%M:%S'))
        print("stare : %s  :%s" % (os.getpid(), proxies))
        data = {
            'query': 'filetype:doc α中尺度',
            'from': 'index-nologin',
            'sugsuv': '1538978449489453',
            'sut': '1325',
            'sugtime': '1538981119303',
            'lkt': '0,0,0',
            's_from': 'index',
            'sst0': '1538981119303',
            'page': '3',
            'ie': 'utf8',
            'p': '40040100',
            'dp': '1',
            'w': '01019900',
            'dr': '1',
        }
        self.my_cookies = ''
        while True:
            new_time_two = datetime.now()
            # 当时间大于8个小时 = 28800 秒的时候重启程序
            time_delete = (new_time_two - new_time).seconds
            if time_delete>28800:
                print(time_delete)
                log_sougou.info("进程关闭：%s 时间差为 ： %s" %(os.getpid(),time_delete))
                sys.exit()
            try:
                # 关键词
                item = li_db_words.find_and_modify({'state': 0}, {'$set': {"state": 8}})
                # item = li_db_words.find_and_modify({'state_sougou': 0}, {'$set': {"state_sougou": 8}})
                if not item:
                    print('程序完结')
                    sys.exit()
                name = item['keyword']
                # name = item['_id']
                # 搜索查询关键词
                for word in ['doc', 'docx', 'pdf', 'ppt', 'pptx', 'rtf']:
                    self.page_num += 1
                    if self.page_num % 70 == 1:
                        self.my_cookies = self.find_cookie(proxies)
                        print("获取新的cookies", self.my_cookies['SNUID'], self.page_num, os.getpid())
                    data['query'] = 'filetype:%s %s' % (word, name)
                    self.find_ones(data, proxies)
            except Exception as e:
                print(e)
                log_sougou.info("error delete_mongo: %s" % (e))

    def md5_generator(self, url):
        return md5(url.encode()).hexdigest()

    def read(self):
        while True:
            try:
                ip_text = requests.get("http://mp.pachongdaili.com/api.php?order=d1546605521").text
                ip_list = re.findall(r'\d+.\d+.\d+.\d+', ip_text, re.S)
                ip_list_one = [{"http": "http://dtip123456:dtip123456@" + str(x).strip() + ":888",
                                "https": "http://dtip123456:dtip123456@" + str(x).strip() + ":888"} for x in ip_list if
                               len(x) > 7]
                if len(ip_list_one) == 10:
                    self.ip_list = ip_list_one
                else:
                    continue
                sleep(1)
            except:
                pass

    def proce(self):
        trader = []
        for i in range(70):
            proxies = self.pro[i + 100]
            pr = Process(target=self.delete_mongo, args=(proxies, i,))
            sleep(0.5)
            pr.start()
            trader.append(pr)
        for i in trader:
            i.join()
        print('proce this is pid: %s' % os.getpid())

    def proce_one(self):
        while True:
            self.proce()


if __name__ == '__main__':
    # print(randint(0,4))
    Insertsql().proce_one()
