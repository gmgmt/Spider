# -*- coding: utf-8 -*-
# @Time    : 2018/7/31 13:43
import os
import sys
path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path)

import datetime
import re
import pymongo
import threading
import hashlib
import requests
import logging
import random
from urllib.parse import urljoin
from multiprocessing import Process, Queue, Pool
from lxml.html import etree
from cnki import env,link_sql
from time import sleep
hm = hashlib.md5()
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36',
        }
db = pymongo.MongoClient(env.MONGODB_URI)[env.MONGODB_NAME]
li_db = db[env.COLLECTION_NAME]
push_time = datetime.datetime.now().strftime('%Y-%m-%d')
logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='./cnki_insert_yuanshuju_sql.log',
                        # encoding='utf-8',
                        filemode='w')
lin_sql = link_sql.Sql()
class Insertsql(object):
    def __init__(self):
        self.pro = self.get_pro()
        super().__init__()

    def get_pro(self):
        db_one = pymongo.MongoClient(env.MONGODB_URI)['proxy']
        li_db_one = db_one['proxies_ip']
        xx_pro = []
        li_db_two = li_db_one.find()
        for i in li_db_two:
            ip = i['ip']
            xx_pro.append({"http":ip})
        return xx_pro

    def find_one(self, item,connects_two, cursor_two, proxies):
        url = item['href_link']
        # item['status'] = 1
        sleep(1)
        A = 0
        try:
            while True:
                A += 1
                if A == 5:
                    return
                try:
                    req = requests.get(url, headers=headers, proxies = proxies, timeout=60)
                    req.close()
                    break
                except Exception as e:
                    print(e)

            if req.status_code == 200:
                try:
                    con_et = etree.HTML(req.content)
                    nr = con_et.xpath('//div[@class="wxTitle"]')[0]
                    title = nr.xpath('//h2[@class="title"]//text()')[0]
                    authors = nr.xpath('//div[@class="author"]/span/a/text()')[0]
                    school = nr.xpath('//div[@class="orgn"]/span/a/text()')[0]
                    try:
                        nr_two = con_et.xpath('//div[@class="wxBaseinfo"]')[0]
                        try:
                            abstrac = nr_two.xpath('//span[@id="ChDivSummary"]/text()')[0]
                        except:
                            abstrac = ''
                        try:
                            keys = nr_two.xpath('//p/label[@id="catalog_KEYWORD"]/following-sibling::a/text()')
                            new_keys = "".join(keys).replace(";  ",',')
                        except:
                            new_keys = ''
                        try:
                            teachers = nr_two.xpath('//p/label[@id="catalog_TUTOR"]/following-sibling::a/text()')
                            new_teachers = "".join(teachers).replace(";  ",',')
                        except:
                            new_teachers = ''
                        try:
                            ztcls = nr_two.xpath('//p/label[@id="catalog_ZTCLS"]/parent::p/text()')[0]
                        except:
                            ztcls = ''
                        #插入元数据
                        nr = (title,authors,school,abstrac,new_keys,new_teachers,ztcls,url,push_time)
                        sql = "insert into "+str(env.yuanshuju_name)+" values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        source = lin_sql.execute_two(sql,nr,connects_two, cursor_two)
                        # 改变mongo属性
                        if source:
                            li_db.update(item, {'$set': {"status": 2}})
                            print("改变mongo")
                    except Exception as e:
                        print(e)
                        logging.error("this is yuanshuju Error: %s"%e)
                        pass
                    # 插入参考文献
                    # self.refer(url,connects_two, cursor_two, proxies)
                except Exception as e:
                    print(e)
                    print("出现错误error::   "+url)
                    sleep(5)
            else:
                print("进入页面错误编码："+str(req.status_code))
        except Exception as e:
            print("error:"+str(e))
            sleep(5)
            pass
    def refer(self,url,connects_two, cursor_two, proxies):
        # 改变三个变量，类型(reftype , CurDBCode)，页数，
        frame_url = url.replace("/detail.aspx", "/frame/list.aspx")
        try:
            article_id = str(url).split("filename=")[1]
        except:
            print("article_id is error")
            return
        for I in [1,3]:
            # type=1 一级参考2 二级参考 3一级引文 4,二级引文
            if I == 1:
                leve = '一级'
                relationship = '参考文献'
            else:
                leve = '一级'
                relationship = '引证文献'
            nr = [article_id,leve,relationship,url]
            for X in ['CJFQ',"CBBD",'SSJD']:
                new_frame_url_cjfq =  str(frame_url) + '&RefType=%s&vl=&CurDBCode=%s&page=%s'%(I,X,1)
                try:
                    self.find_cbbd(new_frame_url_cjfq,nr,X,1,connects_two, cursor_two, proxies)
                except Exception as e:
                    print(e)

    def find_cbbd(self, new_frame_url_cbbd,sql_list,curcode,page,connects_two, cursor_two, proxies):
        sleep(random.randint(0,2))
        req = requests.get(new_frame_url_cbbd, headers=headers,proxies = proxies, timeout=60)
        req.close()
        con_et = etree.HTML(req.content)
        if req.status_code == 200:
            if curcode == 'CJFQ':
                # 除了图书的全部在这
                if page == 1:
                    new_Box_s = con_et.xpath('//div[@class="essayBox"]//div[@class="dbTitle"][text()!="中国图书全文数据库" and text()!="国际期刊数据库"]/parent::div')
                else:
                    new_Box_s = con_et.xpath(
                                        '//div[@class="essayBox"]//div[@class="dbTitle"][text()="中国学术期刊网络出版总库"]/parent::div')
            elif curcode == 'SSJD':
                new_Box_s = con_et.xpath(
                    '//div[@class="essayBox"]//div[@class="dbTitle"][text()="国际期刊数据库"]/parent::div')
            else:
                # 只有图书的
                new_Box_s = con_et.xpath('//div[@class="essayBox"]//div[@class="dbTitle"][text()="中国图书全文数据库"]/parent::div')

            A = 0
            for i in new_Box_s:
                title = i.xpath('.//div[@class="dbTitle"]/text()')[0]
                #判断文件类型
                refer_type = self.find_leixing(title)
                if refer_type:
                    lis = i.xpath('.//ul//li')
                    print("this is len(lis) : %s type: %s  page:%s  filename : %s" % (
                    len(lis), refer_type, page, sql_list[:-1]))
                    logging.info("this is len(lis) : %s type: %s  page:%s  filename : %s" % (
                    len(lis), refer_type, page, sql_list[:-1]))
                    for li in lis:
                        try:
                            refer_url_one = li.xpath('.//@href')[0]
                            refer_url = "http://kns.cnki.net"+str(refer_url_one)
                        except:
                            refer_url = ""
                        refer_texts = li.xpath('.//text()')
                        refer_text = self.replac("".join(refer_texts)).replace("  "," ").strip()
                        # sql 的插入
                        nr =tuple(sql_list+[refer_url,refer_type,refer_text])
                        sql = "insert into "+str(env.refer_name)+"(article_uid,refer_level,relationship,article_url,refer_url" \
                              ",refer_type,refer_text,article_type) values(%s, %s, %s, %s, %s, %s, %s, '博硕士')"
                        lin_sql.execute_two(sql, nr,connects_two, cursor_two)
                    #判断有没有下一页
                    try:
                        next_page = i.xpath('.//span[@name="pcount"]/text()')[0]
                        if int(page*10) < int(next_page):
                            A = 1
                    except:
                        pass
                else:
                    print("没有文件类型")
                    logging.error('this title is not type %s'%new_frame_url_cbbd)
                    continue
            if A == 1:
                #有下一页
                new_page = page+1
                # 修改连接
                new_frame_url_cbbd_two = str(new_frame_url_cbbd).replace('&page=%s'%(page),'&page=%s'%(new_page))
                self.find_cbbd(new_frame_url_cbbd_two,sql_list,curcode,new_page,connects_two, cursor_two, proxies)
            else:
                return

    def replac(self,text):
        return re.sub(r'[&nbsp\r\n]','',text)

    def find_leixing(self,title):
        titles = ['期刊','博士','硕士','图书','会议论文','报纸','网页','专利','标准','年鉴']
        for i in titles:
            if str(title).find(str(i))>-1:
                return i
        return None

    def delete_mongo(self, proxies):
        connects_two, cursor_two = lin_sql.open_two()
        while True:
            try:
                item = li_db.find_and_modify({'status':0}, {'$set': {"status":1}})
                if not item:
                    return
                item['status'] = 1
                self.find_one(item,connects_two, cursor_two, proxies)
            except Exception as e:
                print(e)

    def delete_carw(self, num):
        print('this is pid: %s' % os.getpid())
        threads = []
        proxies = self.pro[num*4:(num+1)*4]
        print(proxies)
        # self.pro.append(proxies)
        for i in range(0, 4):
            pro = proxies[i]
            t = threading.Thread(target=self.delete_mongo, args=(pro,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            # 多线程多join的情况下，依次执行各线程的join方法, 这样可以确保主线程最后退出， 且各个线程间没有阻塞
            t.join()

if __name__ == '__main__':
    ns = Insertsql()
    trader = []
    link_sql.Sql().creat_table()
    for i in range(10):
        pr = Process(target=ns.delete_carw, args=(i,))
        pr.start()
        trader.append(pr)

    for i in trader:
        i.join()



#