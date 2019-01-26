# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 9:53
import os
import sys
import requests,pymongo,datetime,logging
path_this = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path_this)
from time import sleep
from lxml.html import etree
from multiprocessing import Process, Queue, Pool
from hashlib import md5
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
    def __init__(self) -> None:
        self.pro = self.get_pro()
        self.starttime = datetime.datetime.now()
        super().__init__()

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

    def long_mayi(self,username,password,proxies):
        A = 0
        data = {
            'enews': 'login',
            'ecmsfrom': '9',
            'username': username,
            'password': password,
            'Submit': '(unable to decode value)'

        }
        while True:
            A = A + 1
            if A == 5:
                print("请检查账号密码")
                return
            try:
                url = 'http://lib.mayiso.com/e/enews/index.php'
                session = requests.session()
                session.post(url, data=data, headers=headers, proxies = proxies, timeout=120)
                url_ruko = 'http://lib.mayiso.com/e/action/ShowInfo.php?classid=2&id=8'
                req_ro = session.get(url_ruko, headers=headers, proxies = proxies, timeout=120)
                # print(session.cookies.get_dict())
                url_one = str(req_ro.text).split("window.location.href='")[1].split("';")[0]
                req = session.get(url_one, headers=headers, proxies = proxies, timeout=120)
                print(req.cookies.get_dict())
                new_url = 'http://www.cnki.net.www.auth.njfu.edu.cn/old/'
                session.get(new_url, headers=headers, proxies = proxies, timeout=120)
                # print(session.cookies.get_dict())
                new_url_two = 'http://kns.cnki.net.www.auth.njfu.edu.cn/kns/Request/login.aspx?pt=1&p=/kns&td=1540955197584'
                session.get(new_url_two, headers=headers, proxies = proxies,timeout=120)
                if session.cookies.get('ASP.NET_SessionId'):
                    print(session.cookies.get('ASP.NET_SessionId'))
                    return session
            except Exception as e:
                print(e)
        # self.find_url(session)

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

    def find_url(self, session, proxies):
        while True:
            try:
                # endtime = datetime.datetime.now()
                # if (endtime - self.starttime).seconds > 10000:
                #     print("经过时间 : %s"%((endtime - self.starttime).seconds))
                #     print("重新请求session")
                #     logging.info("重新请求session")
                #     self.starttime = datetime.datetime.now()
                #     username = env.mayiusername
                #     password = env.mayipassword
                #     session = self.long_mayi(username, password, proxies)
                    # self.find_url(session, proxies)
                item = li_db.find_and_modify({'status_two': 0}, {'$set': {"status_two": 1}})
                if not item:
                    return
                item['status_two'] = 1
                self.refer_url(session, item, proxies)
            except Exception as e:
                print(e)

    def refer_url(self, session, item, proxies):
        sleep(15)
        A = 0
        # 拼接连接
        url = item['href_link']
        new_url = str(url).replace('http://kns.cnki.net','http://kns.cnki.net.www.auth.njfu.edu.cn')+"&uid=WEEvREcwSlJHSldRa1FhcEE0RVVzYStFOStFWXN2azA0RURmRXFvbFJnYz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!"
        while True:
            A += 1
            if A == 3:
                return
            try:
                req = session.get(new_url, headers=headers, proxies = proxies, timeout=120)
                req.close()
                break
            except Exception as e:
                logging.error(e)
                print(e)
        if req.status_code == 200:
            breq_et = etree.HTML(req.content)
            down_link = breq_et.xpath('.//div[@id="DownLoadParts"]/a[@class="icon icon-dlGreen"]/@href')[0]
            if down_link:
                #下载文档caj格式
                A = 0
                while True:
                    A += 1
                    if A == 4:
                        username = env.mayiusername
                        password = env.mayipassword
                        session = self.long_mayi(username, password, proxies)
                        self.find_url(session, proxies)
                    try:
                        req_text = session.get(down_link, headers=headers, proxies = proxies, timeout=360)
                        name_nowTime = datetime.datetime.now().strftime('%Y%m%d')
                        path = str(env.file_caj_path + str(name_nowTime))
                        file_na = self.open(path)
                        if file_na:
                            if req_text.status_code == 200:
                                fulltext_name = str(url).split('filename=')[-1].strip()
                                new_name = self.md5_generator(url)
                                new_path = str(path) + "/" + new_name + ".caj"
                                fo = open(new_path, 'wb')
                                fo.write(req_text.content)
                                fo.close()
                                print("下载caj文件")
                                break
                    except Exception as e:
                        logging.error(e)
                        print(e)

                # 插入数据库
                nr = (url, fulltext_name, new_path)
                sql = "insert into "+str(env.quanwen_name)+" values(%s, %s, %s)"
                source = insert_sql.inset_fulltext(sql,nr)
                print('find_url is pid: %s' % os.getpid())

                #改变mongo属性
                if source:
                    li_db.update(item, {"$set": {"status_two": 2}})
                    print("改变mongo")
        else:
            print("访问错误")

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
        for i in range(20):
            proxies = self.pro[i]
            print(proxies)
            username = env.mayiusername
            password = env.mayipassword
            session = self.long_mayi(username, password, proxies)
            sleep(2)
            pr = Process(target=self.find_url, args=(session, proxies))
            pr.start()
            trader.append(pr)

        for i in trader:
            i.join()
            # i.start()
            # i.terminate()

if __name__ == '__main__':
    my = Mayiso()
    my.allpol()
    # 用户名,密码
