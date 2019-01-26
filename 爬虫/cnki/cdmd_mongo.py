# -*- coding: utf-8 -*-
# @Time    : 2018/7/30 14:06
'''
获取目录代码
'''
import os
import sys
path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path)
import logging
from time import sleep
import time
import requests
from bs4 import BeautifulSoup
import random
import re
from urllib.parse import urljoin
from lxml.html import etree
from cnki import env,zd
from multiprocessing import Process, Queue, Pool
import pymongo
import threading
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
        self.pro = self.get_pro()[15:30]

    def get_pro(self):
        db_one = pymongo.MongoClient(env.MONGODB_URI2)['proxy']
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

    def find_list(self, url):#先解析一级目录
        res_nr = requests.get(url, headers = headers, timeout = 120)
        res_nr.close()
        if res_nr.status_code == 200:
            breq_et = etree.HTML(res_nr.content)
            liks = breq_et.xpath('//div[@class="leftlist_1"]/@id')
            return liks
        else:
            print("目录获取失败")
            return

    def find_two_list(self, one_list,two_list):
        if len(one_list)%100 == 0:
            print("this is pid: %s  one_list: %s two_list: %s"%(os.getpid(),len(one_list),len(two_list)))
            logging.info("this is pid: %s  one_list: %s two_list: %s"%(os.getpid(),len(one_list),len(two_list)))
        if len(one_list) == 0:
            # 多线程
            threads = []
            for i in range(7):
                # print(self.pro)
                proxies = self.pro.pop(0)
                t = threading.Thread(target=self.delete_carw, name='LoopThread_%s'% i,args=(two_list,proxies))
                threads.append(t)
            for t in threads:
                t.start()
            return
        url = 'http://epub.cnki.net/kns/request/NaviGroup.aspx'
        value = one_list.pop(0)
        data = {'code':value,
                'tpinavigroup':'CDMDtpiresult',
                'catalogName':'',
                '__':'%s %s' % (time.strftime('%a %b %d %Y %H:%M:%S GMT+0800'), ' (中国标准时间)')}
        try:
            res_nr = requests.get(url, headers = headers, params = data, timeout = 120)
            res_nr.close()
            if res_nr.status_code == 200:
                breq_et = etree.HTML(res_nr.content)
                inputs = breq_et.xpath('//input[@type="checkbox" and @id="selectbox"]')
                if len(inputs) == 0:
                    print("目录获取失败")
                    pass
                for input in inputs:
                    value_two = input.xpath('./@value')[0]
                    try:
                        name = input.xpath('./@name')[0]
                        one_list.append(value_two)
                    except:
                        two_list.append(value_two)
            else:
                print("目录获取失败")
                logging.error("目录获取失败")
        except Exception as e:
            print(e)
        self.find_two_list(one_list,two_list)



    def delete_carw(self, pid_list, proxies):
        while True:
            try:
                pid = pid_list.pop(0)
                self.find_url(pid,proxies,0)
            except Exception as e:
                if len(pid_list) == 0:
                    print("pid len is 0 end")
                    logging.info("pid len is 0 end")
                    return
                print(e)
                logging.error(e)


    def find_url(self,item,proxies,num):
        session = self.get_session()
        data = {'action': '',
                'NaviCode': 'A001_4',
                'ua': '1.25',
                'PageName': 'ASP.brief_result_aspx',
                'DbPrefix': 'CDMD',
                'DbCatalog': '中国优秀博硕士学位论文全文数据库',
                'ConfigFile': 'CDMD.xml',
                'db_opt': '中国优秀博硕士学位论文全文数据库',
                'db_value': '中国博士学位论文全文数据库,中国优秀硕士学位论文全文数据库',
                'his': '0',
                '__': '%s %s' % (time.strftime('%a %b %d %Y %H:%M:%S GMT+0800'), ' (中国标准时间)')}
        data['NaviCode'] = str(item)
        session.post('http://kns.cnki.net/kns/request/SearchHandler.ashx', headers=headers,proxies = proxies, data=data, timeout=120)
        url_two = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_result_aspx&isinEn=0&dbPrefix=CDMD&dbCatalog=%e4%b8%ad%e5%9b%bd%e4%bc%98%e7%a7%80%e5%8d%9a%e7%a1%95%e5%a3%ab%e5%ad%a6%e4%bd%8d%e8%ae%ba%e6%96%87%e5%85%a8%e6%96%87%e6%95%b0%e6%8d%ae%e5%ba%93&ConfigFile=CDMD.xml&research=off&t=1540776013588&keyValue=&S=1&sorttype='
        res_nr = session.get(url_two,headers = headers,proxies = proxies, timeout = 120)
        res_nr.close()
        # 解析入库
        print("this is code  :  %s"%(item))
        if res_nr.status_code == 200:
            breq_et = etree.HTML(res_nr.content)
            hrefs = breq_et.xpath('.//a[@class="fz14"]/@href')
            # #  论文级别
            # jibie = breq_et.xpath('//table[@class="GridTableContent"]/tbody//tr[2]/td[5]/text()')
            # print('级别：',jibie)
            # #   作者
            # author = breq_et.xpath('//table[@class="GridTableContent"]/tbody//tr[2]/td[3]//text()')
            # print('作者：',author)
            # #    作者代码
            # daima = breq_et.xpath('')
            if len(hrefs) == 0:
                logging.error("第一页错误 ：%s"%item)
                print("第一页错误 ：%s"%item)
                return
            for i in hrefs:
                new_url = "http://kns.cnki.net/KCMS/"+str(i).replace("/kns/","")
                #把连接放进mongo中
                # pattern = re.compile(r'fileName=(.*)',re.S)
                # uid = re.findall(pattern,new_url)
                # print(uid)
                # res = requests.get(new_url)
                # detil_page = etree.HTML(res.content)
                # # 导师
                # teacher = breq_et.xpath('//label[@id="catalog_TUTOR"]/following-sibling::a/text()').pop()
                # print('导师：',teacher)
                # #   导师代码
                # #学位授予单位
                # school = breq_et.xpath('//div[@class="sourinfo"]/p[1]/a[1]/text()')
                # print('学校：',school)
                # #  学位授予单位代码
                # #   学科专业
                # BoShu_cn = detil_page.xpath('//p[@class="title"]//text()')
                # print(BoShu_cn)
                # BoShu_en = detil_page.xpath('//p[@class="title"]/following-sibling::p[1]//text()')
                # print(BoShu_en)
                # isSci = 'false'
                # isEi = 'false'
                # isCore = 'true'
                # issn = detil_page.xpath('//p[@class="title"]/following-sibling::p[3]//text()').split(':')[1]
                # print(issn)

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
            self.next_page(session,page_num, proxies, item)
        elif res_nr.status_code == 404:
            return

    def next_page(self,session,page_num, proxies, item):
        sleep(random.randint(2,5))
        page_url = "http://kns.cnki.net/kns/brief/brief.aspx?curpage="+str(page_num)+"&RecordsPerPage=50&QueryID=0&ID=&turnpage=1&tpagemode=L&dbPrefix=CDMD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0"
        res_nr = session.get(page_url, headers=headers,proxies = proxies, timeout=60)
        res_nr.close()
        # 解析入库
        if res_nr.status_code == 200:
            breq_et = etree.HTML(res_nr.content)
            hrefs = breq_et.xpath('.//a[@class="fz14"]/@href')
            logging.info("pid :  %s   url_page: %s    len(hrefs) : %s"%(item,page_num,len(hrefs)))
            if len(hrefs) == 0:
                if str(res_nr.text).find("请输入验证码")>-1:
                    # 从第一页重新请求
                    self.find_url(item,proxies,page_num)
            for i in hrefs:
                new_url = "http://kns.cnki.net/KCMS/" + str(i).replace("/kns/", "")
                # 把连接放进mongo中
                self.insert_mongo(new_url)
            next_page = breq_et.xpath('//div[@class="TitleLeftCell"]//a/text()')
            if ("".join(next_page).find("下一页") > -1):
                self.next_page(session, page_num + 1, proxies, item)
            else:
                return

    def insert_mongo(self, new_url_one):
        new_url_two = re.sub(r'&QueryID=\d+','',new_url_one)
        new_url =  re.sub(r'&CurRec=\d+','',new_url_two)
        save, find = self.zd.zdf()
        find["href_link"] = str(new_url)
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
    url = "http://epub.cnki.net/kns/brief/result.aspx?dbPrefix=CDMD"
    one_list = pe.find_list(url)
    print("获取一级目录: %s"%(one_list))
    two_list = []
    pe.find_two_list(one_list,two_list)




