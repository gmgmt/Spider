# -*- coding: utf-8 -*-
# @Time    : 2018/7/31 15:54
ENV = ""
# 增量或全量
all_update = 1

# mongo的连接
COLLECTION_NAME = 'cnki_cdmd'

MONGODB_URI2 = 'mongodb://192.168.8.211:27017'
# MONGODB_NAME = "cnki_wbw"
MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_NAME = "one"
# 存放文件的路径
file_caj_path = "F:\cnkiCDMD\\"
file_caj_path_pdf = "D:\cnkiCDMD_pdf\\"

#sql 的配置
# path = '192.168.8.212'
# name = 'sa'
# password = '123456'
# sql_name = 'cnki_cdmd'
# 元数据表名
yuanshuju_name = "cnki_cdmd_yuanshuju_20181030"
#引文数据表名
refer_name  = 'cnki_cdmd_reference_20181030'
# 全文表名
quanwen_name = 'cnki_cdmd_fulltext_20181105'
# "192.168.2.213","sa","Bigsearch@","pub"
#蚂蚁的用户名和密码
mayiusername = 'iampber'
mayipassword = 'xueshuyi1@'