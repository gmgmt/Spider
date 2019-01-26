# -*- coding: utf-8 -*-
# @Time    : 2018/7/31 16:07
from cnki import env
import logging
# import pyodbc
import pymssql
from time import sleep

class Sql(object):
    def __init__(self):
        self.open()
        super().__init__()
    def close(self):
        self.cursor_two.close()
        self.connects_two.close()

    def open(self):
        self.connects_two = pymssql.connect(env.path, env.name, env.password, env.sql_name,charset='utf8')
        self.cursor_two = self.connects_two.cursor()

    def open_two(self):
        connects_two = pymssql.connect(env.path, env.name, env.password, env.sql_name,charset='utf8')
        cursor_two = connects_two.cursor()
        return connects_two,cursor_two

    def select_two(self, sql):
        try:
            self.cursor_two.execute(sql)
            result = self.cursor_two.fetchone()
            return result[0]
        except Exception as e:
            print(e)
            # logging.error("error " + str(e))
            # logging.error("error "+sql)
    def inset_fulltext(self,sql,nr):
        try:
            self.cursor_two.execute(sql,nr)
            self.connects_two.commit()
            print("插入数据库")
            return True
        except Exception as e:
            if str(e).find("2627")>-1:
                return True
            print(e)
            return False
    def execute_two(self,sql,nr,connects_two,cursor_two):
        try:
            cursor_two.execute(sql,nr)
            connects_two.commit()
            print("插入数据库")
            return True
        except Exception as e:
            if str(e).find("2627")>-1:
                return True
            print(e)
            return False
            # logging.error(e)
            # logging.error("error "+sql)
    def creat_fulltext(self):
        sql = "CREATE TABLE [dbo].[%s] (\
                [url] nvarchar(900) NOT NULL ,\
                [filename] nvarchar(200) NOT NULL ,\
                [path] nvarchar(200) NOT NULL \
                );\
                ALTER TABLE [dbo].[%s] ADD PRIMARY KEY ([url]);"%(env.quanwen_name,env.quanwen_name)
        try:
            self.cursor_two.execute(sql)
            self.connects_two.commit()
            print("新建表")
        except Exception as e:
            print(str(e))
            print("if 2714 表已经有了")
        self.close()
        self.open()

    def creat_table(self):
        sql =  "CREATE TABLE [dbo].[%s] (\
                [article_uid] nvarchar(200) NOT NULL ,\
                [article_type] nvarchar(200) NOT NULL ,\
                [article_url] nvarchar(1000) NOT NULL ,\
                [relationship] nvarchar(200) NULL ,\
                [refer_url] nvarchar(900) NULL ,\
                [refer_type] nvarchar(200) NULL ,\
                [refer_text] nvarchar(MAX) NULL ,\
                [refer_level] nvarchar(10) NULL \
                );\
                CREATE TABLE [dbo].[%s] (\
                [题名] nvarchar(MAX) NULL ,\
                [作者] nvarchar(255) NULL ,\
                [学校] nvarchar(255) NULL ,\
                [摘要] nvarchar(MAX) NULL ,\
                [关键词] nvarchar(MAX) NULL ,\
                [导师] nvarchar(255) NULL ,\
                [分类号] nvarchar(255) NULL ,\
                [url] nvarchar(255) NOT NULL ,\
                [insertTime] nvarchar(255) NULL \
                );\
                ALTER TABLE [dbo].[%s] ADD PRIMARY KEY ([url]);"%(env.refer_name,env.yuanshuju_name,env.yuanshuju_name)
        try:
            self.cursor_two.execute(sql)
            self.connects_two.commit()
            print("新建表")
        except Exception as e:
            print(str(e))
            print("if 2714 表已经有了")
        self.close()
        # self.open()





