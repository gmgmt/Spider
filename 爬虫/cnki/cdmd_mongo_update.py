# -*- coding: utf-8 -*-
# @Time    : 2018/7/30 14:06
import os
import sys
path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path)
import logging
import threading
import pymongo
import time, re
import requests
import random,datetime
from urllib.parse import urljoin
from lxml.html import etree
from cnki import env,zd
from multiprocessing import Process, Queue, Pool
from time import sleep
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36',
            # 'Cookie': 'Ecp_ClientId=5181017152501184119; cnkiUserKey=aae383e8-2b0b-c2bb-4b58-3f935cade3b9; UM_distinctid=16680ece2f145e-0951d627dfca38-504b2518-1fa400-16680ece2f63ab; Ecp_IpLoginFail=181024219.140.11.22; RsPerPage=50; _pk_ses=*'
        }

db = pymongo.MongoClient(env.MONGODB_URI)[env.MONGODB_NAME]
li_db = db[env.COLLECTION_NAME]

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='./cnki.log',
                        # encoding='utf-8',
                        filemode='w')
A = 0
class Persee(object):
    def __init__(self):
        self.zd = zd.zd()
        self.all_update = env.all_update
        # self.logger = logging.getLogger("cnki_mongo")
        self.pro = self.get_pro()[15:30]

    def get_pro(self):
        db_one = pymongo.MongoClient(env.MONGODB_URI)['proxy']
        li_db_one = db_one['proxies_ip']
        xx_pro = []
        li_db_two = li_db_one.find()
        for i in li_db_two:
            ip = i['ip']
            xx_pro.append({"http":ip})
        return xx_pro

    def get_session(self):
        session = requests.session()
        url = 'http://kns.cnki.net/kns/request/NaviGroup.aspx'
        data_one = {'code': 'A',
                    'tpinavigroup': 'CDMDtpiresult',
                    'catalogName': '',
                    '__': '%s %s' % (time.strftime('%a %b %d %Y %H:%M:%S GMT+0800'), ' (中国标准时间)')}
        session.get(url, headers=headers, params=data_one, timeout=120)
        session.cookies.set('RsPerPage', '50')
        return session

    def month_get(self):
        d = datetime.datetime.now()
        dayscount = datetime.timedelta(days=d.day)
        dayto = (d - dayscount).strftime('%Y-%m-%d')
        return dayto
        # date_from = datetime.datetime(dayto.year, dayto.month, 1, 0, 0, 0)
        # date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
        # print('---'.join([str(date_from), str(date_to)]))



    def find_url(self,num):
        session = self.get_session()
        new_time = time.strftime('%Y-%m-%d')

        data = {'action':'',
                'NaviCode':'*',
                'ua':'1.21',
                'isinEn':'0',
                'PageName':'ASP.brief_result_aspx',
                'DbPrefix':'CDMD',
                'DbCatalog':'中国优秀博硕士学位论文全文数据库',
                'ConfigFile':'CDMD.xml',
                'db_opt':'CDMD',
                'db_value':'中国博士学位论文全文数据库,中国优秀硕士学位论文全文数据库',
                'updatedateN_from':self.month_get(),
                'updatedateN_to':new_time,
                'updatedateN_opt':'month',
                'his':'0',
                '__': '%s %s' % (time.strftime('%a %b %d %Y %H:%M:%S GMT+0800'), ' (中国标准时间)')}
        session.post('http://kns.cnki.net/kns/request/SearchHandler.ashx', headers=headers, data=data, timeout=120)
        url_two = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_result_aspx&isinEn=0&dbPrefix=CDMD&dbCatalog=%e4%b8%ad%e5%9b%bd%e4%bc%98%e7%a7%80%e5%8d%9a%e7%a1%95%e5%a3%ab%e5%ad%a6%e4%bd%8d%e8%ae%ba%e6%96%87%e5%85%a8%e6%96%87%e6%95%b0%e6%8d%ae%e5%ba%93&ConfigFile=CDMD.xml&research=off&t=1540882620494&keyValue=&S=1&sorttype='
        res_nr = session.get(url_two,headers = headers, timeout = 120)
        res_nr.close()
        # 解析入库
        if res_nr.status_code == 200:
            breq_et = etree.HTML(res_nr.content)
            hrefs = breq_et.xpath('.//a[@class="fz14"]/@href')
            if len(hrefs) == 0:
                print("第一页错误")
                return
            for i in hrefs:
                new_url = "http://kns.cnki.net/KCMS/"+str(i).replace("/kns/","")
                #把连接放进mongo中
                self.insert_mongo(new_url)
            next_page = breq_et.xpath('//div[@class="TitleLeftCell"]//a/@href')
            if len(next_page) == 0:
                # 如果没有下一页则跳出
                return
        #     翻页
            if num == 0:
                page_num = 2
            else:
                page_num = num
            self.next_page(session, page_num)
        elif res_nr.status_code == 404:
            return
    def next_page(self,session,page_num):
        sleep(random.randint(0,3))
        # page_url = "http://kns.cnki.net/kns/brief/brief.aspx?curpage="+str(page_num)+"&RecordsPerPage=50&QueryID=8&ID=&turnpage=1&tpagemode=L&dbPrefix=CDMD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&sKuaKuID=8&isinEn=0"
        page_url = "http://kns.cnki.net/kns/brief/brief.aspx?curpage="+str(page_num)+"&RecordsPerPage=50&QueryID=3&ID=&turnpage=1&tpagemode=L&dbPrefix=CDMD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0"
        res_nr = session.get(page_url, headers=headers, timeout=60)
        res_nr.close()
        # 解析入库

        if res_nr.status_code == 200:
            breq_et = etree.HTML(res_nr.content)
            hrefs = breq_et.xpath('.//a[@class="fz14"]/@href')
            logging.info("一月  url_page: %s    len(hrefs) : %s"%(page_num,len(hrefs)))
            if len(hrefs) == 0:
                if str(res_nr.text).find("请输入验证码")>-1:
                    # 从第一页重新请求
                    self.find_url(page_num)

            for i in hrefs:
                new_url = "http://kns.cnki.net/KCMS/" + str(i).replace("/kns/", "")
                # 把连接放进mongo中
                self.insert_mongo(new_url)
            next_page = breq_et.xpath('//div[@class="TitleLeftCell"]//a/text()')
            if("".join(next_page).find("下一页")>-1):
                self.next_page(session, page_num + 1)
            else:
                return

    def insert_mongo(self, new_url_one):
        new_url_two = re.sub(r'&QueryID=\d+', '', new_url_one)
        new_url = re.sub(r'&CurRec=\d+', '', new_url_two)
        save, find = self.zd.zdf()
        find["href_link"] = str(new_url)
        # 可以修改
        le = li_db.find(find).count()
        if le == 0:
            save["href_link"] = str(new_url)
            li_db.insert(save)
            print("插入mongo")
        else:
            pass
            print("已有")

if __name__ == '__main__':

    pe = Persee()
    pe.find_url(0)





