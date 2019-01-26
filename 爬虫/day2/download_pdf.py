# -*- coding: utf-8 -*-
# @Time    : 2018/11/30 14:06

import requests
import datetime
from  multiprocessing import Process, Pool
import pymongo
import os

import time
import threading
import urllib.request
client=pymongo.MongoClient('192.168.8.211',27017)
db=client['experiment']
table=db['day4_tb']



def is_chinese(uchar):
    if uchar >= u'\u4E00' and uchar <= u'\u9fff':
        return True
    else:
        return False

def is_english(uchar):
    if (uchar >= u'\u0041' and uchar <= u'\u005A') or (uchar >= u'\u0061' and uchar <= u'\u007A'):
        return True
    else:
        return False


def find_str(zifuchuan):
    # data=table.find({},{"title":1})
    # zifuchuan=data["title"]
    # new_zifu = zifuchuan[:int(len(zifuchuan)*0.5)]
    new_zifu=zifuchuan
    if not new_zifu:
        return True
    china_num = 0
    english_num = 0
    th_num = 0
    for i in new_zifu:
        # 除字符
        if i.isalpha():
            if is_english(i):
                english_num += 1
            elif is_chinese(i):
                china_num += 1
            else:
                th_num =1
                break
    if th_num:
        print("小语种")
        return False

    elif english_num>china_num:

        print("英文")
        return True
    elif china_num>=english_num:

        print("中文")
        return True
    else:
        print("不是中英文")
        return False

def xiazai():
    # n = 1
    while 1:
        data=table.find_one_and_update({"state": 0}, {"$set": {"state": 1}})
        zifu=data["title"]
        if find_str(zifu)==True:
        # print(data)
            if not data:
                print("全部下载完成")
                break
            # data["state"]= 1
            url=data['url']
            md5=data["url_md5"]
            try:
                static = time.time()
                r = requests.get(url, timeout=5,)
                end = time.time()
                print(end - static)
                size = len(r.content)
                try:
                    if size > 20000:
                        path=os.path.join(r"D:\\",datetime.datetime.now().strftime("%Y-%m-%d"),data["url_md5"][0], data["url_md5"][1:3])
                        try:
                            if not os.path.exists(path):
                                pass
                                # os.makedirs(path)
                        except:
                            pass
                        pathtwo=path + "\\" + md5 + ".pdf"
                        # print()
                    # print(size)
                        with open(pathtwo, 'wb', ) as f:
                            # f.write(r.content)
                            print("下载成功，保存位置：%s" % path)
                    else:
                        print("小于20K")
                        continue
                except:
                    pass
            except:
                table.find_one_and_update({"url_md5": md5}, {"$set": {"state": -1}})
                print("此链接未爬取：%s，%s" % (md5, url))
        else:
            continue

def main():
    pool = Pool(2)
    for i in range(15):
        pool.apply_async(xiazai,)
    pool.close()
    pool.join()
if __name__=="__main__":
    # for a in table.find({}, {"title": 1}):
    #     b=a.get("title")
    #     find_str(b)
    main()





