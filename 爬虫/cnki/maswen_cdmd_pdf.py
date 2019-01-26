# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 9:53
import os
import sys
import requests,pymongo,datetime,logging
path_this = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path_this)
from time import sleep
from selenium import webdriver
from lxml.html import etree
from multiprocessing import Process, Queue, Pool
from hashlib import md5
from urllib.parse import urljoin
from time import sleep
from cnki import env,link_sql
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36',
        }
logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='./cnki_dowm_pdf.log',
                        # encoding='utf-8',
                        filemode='w')
db = pymongo.MongoClient(env.MONGODB_URI)[env.MONGODB_NAME]
li_db = db[env.COLLECTION_NAME]
insert_sql = link_sql.Sql()
starttime = ''
class Mayiso(object):
    def __init__(self):
        self.pro = self.get_pro()
        self.B = 0
        # self.session,self.LID = self.get_LID()

    def open_firefox(self):
        wait_time = 1
        while True:  # 浏览器向url地址发送请求
            try:
                profile = webdriver.ChromeOptions()
                prefs = {
                    'profile.default_content_setting_values': {
                        'images': 2,
                        #'javascript': 2,
                        # 'css': 2
                    }}
                # profile.add_experimental_option('prefs',prefs)
                # profile.add_argument('--headless')# 不弹出浏览器界面
                # profile.add_argument("'--proxy-server={}".format(proxy))
                self.browser = webdriver.Chrome(chrome_options=profile)
                self.browser.get("http://www.maswen.net.cn/web/index.action")
                more_page_btn = self.browser.find_element_by_xpath('//div[@class="box zhuantiBox zhuantiBox1"]//li[@class="one"]')
                more_page_btn.click()
                sleep(1)
                self.browser.find_element_by_xpath('//div[@class="wx"]//li[@id="CDMD"]').text()
                self.browser.find_element_by_xpath("//a[@id='Ecp_header_english']").click()
                self.browser.get_cookies()
                break
            except Exception as e:
                print('尝试打开浏览器失败，重新尝试！Error information:', e, '\t[%s]s latter,try connection again!' % wait_time)
                try:
                    self.browser.quit()
                except:
                    pass
                sleep(wait_time)
                wait_time <<= 1
                if wait_time >= 628:
                    print('This file can\'t cralw!')
                    self.permit = False
                    return


    def get_LID(self, proxies):
        self.open_firefox()
        session = requests.session()
        url = 'http://kns.cnki.net/kns/logindigital.aspx?ParentLocation=http://www.cnki.net'
        data = {
            '__VIEWSTATE': '/wEPDwULLTIxMzE4NjUyNThkZLXwULDTk04PwfjHrahEulA4N5PANUoyc0ijXqyrEpZ+',
            'username':'sh0772',
            'password':'sh0772'
        }
        session.post(url, headers=headers, data=data, timeout=360)
        try:
            LID = session.cookies.get_dict()['LID']
            session.cookies.set("__utma", "263217362.709931502.1543826294.1543826294.1543826294.1")
            session.cookies.set("__utmc", "263217362")
            session.cookies.set("__utmz", "263217362.1543826294.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)")
            session.cookies.set("__utmt", "1")
            session.cookies.set("__utmb", "263217362.2.10.1543826294")
            print(LID)
            return session,LID
        except:
            return None,None

    def get_pro(self):
        try:
            db_one = pymongo.MongoClient(env.MONGODB_URI)['proxy']
            li_db_one = db_one['proxies_ip']
            xx_pro = []
            li_db_two = li_db_one.find()
            for i in li_db_two:
                ip = i['ip']
                xx_pro.append({"http":ip})
            return xx_pro
        except Exception as e:
            print("未连上mongo")
            return

    def restart_program(self):
        try:
            python = sys.executable
            print('三秒后重启')
            sleep(3)
            logging.info("已经重启")
            # print(sys.path[0])
            print(python)
            loc_path = sys.path[0]+"\\mayiso.py"
            print(loc_path)
            os.execl(python, python, loc_path)
        except Exception as e:
            print(e)

    def find_url(self, proxies):
        self.B = 0
        print('find_url is pid: %s' % os.getpid())
        session,LID = self.get_LID(proxies)
        if session:
            while True:
                try:
                    item = li_db.find_and_modify({'status_two': 0}, {'$set': {"status_two": 1}})
                    if not item:
                        return
                    item['status_two'] = 1
                    self.refer_url(item, proxies, session, LID)
                except Exception as e:
                    print(e)

    def refer_url(self, item, proxies, session, LID):
        sleep(8)
        A = 0
        # 拼接连接
        url = item['href_link']
        new_url = str(url).replace('http://kns.cnki.net/KCMS','http://oversea.cnki.net/kcms')+"&uid=%s"%(LID)
        while True:
            A += 1
            if A == 3:
                return
            try:
                req = requests.get(new_url, headers=headers,  timeout=360)
                req.close()
                break
            except Exception as e:
                logging.error(e)
                print(e)

        if req.status_code == 200:
            breq_et = etree.HTML(req.content)
            #new_down_link = breq_et.xpath('.//div[@id="nav"]//li[@class="\n                  pdf\n                "]//@href')[0].strip()
            try:
                new_down_link = breq_et.xpath('.//div[@id="nav"]//li/a/@href')[-3].strip()
            except:
                print("没有找到连接")
                return
            if new_down_link.find('dflag=pdfdown') > -1:
                down_link = urljoin(new_url, new_down_link)
            else:
                logging.error("not down_link  url  :%s"%(new_url))
                return
            if down_link:
                #下载文档caj格式
                A = 0
                while True:
                    A += 1
                    if A == 4:
                        return
                    try:
                        headers_two = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'Host': 'oversea.cnki.net',
                            'Referer': '%s'%new_url,
                            'Upgrade-Insecure-Requests': '1',
                        }
                        req_text = session.get(down_link, headers=headers_two,  timeout=360)
                        name_nowTime = datetime.datetime.now().strftime('%Y%m%d')
                        path = str(env.file_caj_path_pdf + str(name_nowTime))
                        file_na = self.open(path)
                        if file_na:
                            if req_text.status_code == 200:
                                fulltext_name = str(url).split('filename=')[-1].strip()
                                new_name = self.md5_generator(url)
                                new_path = str(path) + "\\" + new_name + ".pdf"
                                fo = open(new_path, 'wb')
                                fo.write(req_text.content)
                                fo.close()
                                print("下载pdf文件 :%s"%(os.getpid()))
                                break
                    except Exception as e:
                        logging.error(e)
                        sleep(2)
                        print(e)
                size_TN = self.getDocSize(new_path)
                # 插入数据库
                if size_TN:
                    self.B = 0
                    nr = (url, fulltext_name, new_path)
                    sql = "insert into "+str(env.quanwen_name)+" values(%s, %s, %s)"
                    source = insert_sql.inset_fulltext(sql,nr)
                    #改变mongo属性
                    if source:
                        li_db.update(item, {"$set": {"status_two": 2}})
                        print("改变mongo")
                else:
                    self.B += 1
                    if self.B >= 5:
                        print('连续超过五次没有正常文件 :%s'%(os.getpid()))
                        self.find_url(proxies)
                        return
                    return
        else:
            print("访问错误")

    def getDocSize(self, path):
        try:
            size = os.path.getsize(path)
            if size<14000:
                print('%s 文件小于13k'%(path.split('\\')[-1]))
                return False
            return True
        except Exception as err:
            print(err)
            return  False

    def md5_generator(self,url):
        """
        生成md5
        :param url:
        :param data:
        :param end_time:
        :return:
        """
        return md5(url.encode()).hexdigest()

    def open(self, path):
        #新建文件夹
        isExists = os.path.exists(path)
        # 调用函数
        if not isExists:
            try:
                os.makedirs(path)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return True

    def allpol(self):
        insert_sql.creat_fulltext()
        trader = []
        for i in range(1):
            proxies = self.pro[i]
            print(proxies)
            pr = Process(target=self.find_url, args=(proxies,))
            pr.start()
            trader.append(pr)

        for i in trader:
            i.join()
            # i.start()
            # i.terminate()

if __name__ == '__main__':
    my = Mayiso()
    my.allpol()
    # my.open_firefox()
    # 用户名,密码
