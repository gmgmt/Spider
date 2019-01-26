# -*- coding: utf-8 -*-
# @Time    : 2018/11/22 15:00
import pymongo
import pymssql
from requests import codes
import requests
import hashlib
from multiprocessing.pool import Pool
from lxml import etree


server="192.168.8.212"
user="sa"
password="123456"

con=pymssql.connect(server,user,password,"Search")
cursor=con.cursor()

cursor.execute('''
IF OBJECT_ID('table_1', 'U') IS NOT NULL
    DROP TABLE table_1
CREATE TABLE table_1 (
    id VARCHAR (20,
    title NVARCHAR (4000),
    author NVARCHAR (4000),
    patent number VARCHAR (100),
    page VARCHAR (100),
    abstract NVARCHAR (max),
    researchDirection NVARCHAR (4000),
    data NVARCHAR (25),
    url VARCHAR (255),
    md5 VARCHAR (255),
    PRIMARY KEY(id)
)
''')


client = pymongo.MongoClient('localhost', 27017)
db = client['day9']
table = db['day9_tb']


def get_html(url):
    try:
        r = requests.get(url)
        if codes.ok == r.status_code:
            return r.text
    except requests.ConnectionError:
        return None

def md5_Encode(url_1):
    #  创建md5对象
    m = hashlib.md5()
    #  传入需要加密的字符串
    m.update(url_1.encode("utf8"))
    #  返回加密之后的字符串
    # print('pppppp')
    return m.hexdigest()



def download_url():
    while 1:
        data = table.find_one_and_update({"state": 0}, {"$set": {"state": 1}})  # 替换MongoDB中的第一个匹配的数据
        # 此函数匹配第一个参数，若存在，则用第二个替换，若无匹配则反回None
        if not data:
            # 如果替换则表示已下载，not None为True,跳出循环
            return
        data["state"] = 1
        # print('当前已搜索%d条数据' % db.day6_tb.find({'state': 1}).count())
        url = data["url"]
        # print(url)
        html = get_html(url=url)
        # print(html)
        content = etree.HTML(html)
        try:
            #   标题加作者
            titles = content.xpath('//table[@id="doctable"]//tr[1]//text()')
            # print(titles)
            # print(titles[0])
            # 标题
            # title = (titles[0],)
            title = (titles[0])
            # print(title)
            # 作者 作者单位
            # author = (titles[1],)
            author = (titles[1])
            # print(author)
            #   pdf链接
            pdfs = content.xpath('//table[@id="doctable"]//a/@href')
            pdf = pdfs[0]
            pdf1 = (pdfs[0],)
            # print((pdfs[0],))
            #  抽象
            abstract = content.xpath('//td[contains(text(),"Abstract:")]/following-sibling::td/text()')
            abstract = abstract[0].strip()
            abstract = (abstract,)
            # print((abstract,))
            #  发布日期
            data = content.xpath('//td[contains(text(),"Publication Date:")]/following-sibling::td/text()')
            data = data[0].strip()
            data = (data,)
            # print((data,))
            #   文件编号
            number = content.xpath('//td[contains(text(),"Document ID:")]/following-sibling::td/div/text()')
            number = number[0].strip()
            number = (number,)
            # print((number,))
            #   学科类别
            researchDirection = content.xpath('//td[contains(text(),"Subject Category:")]/following-sibling::td/text()')
            researchDirection = researchDirection[0].strip()
            researchDirection = (researchDirection,)
            # print((researchDirection,))
            #   专利号
            number_2 = content.xpath('//td[contains(text(),"Report/Patent Number:")]/following-sibling::td/text()')
            number_2 = number_2[0].strip()
            number_2 = (number_2,)
            # print((number_2,))
            #   页码
            page = content.xpath('//td[contains(text(),"Description:")]/following-sibling::td/text()')
            # print(page[0])
            b = str(page[0])
            # c = (b.split(';')[0].strip(),)
            c = (b.split(';')[0].strip())
            c = (c,)
            # print(c)
            md5 = md5_Encode(pdf)
            md5 = (md5,)
            print('222')
            cursor.executemany(
                "INSERT INTO table_1 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [pdf1, md5, number, title, number_2, author, c, abstract, researchDirection, data])
            # 你必须调用 commit() 来保持你数据的提交如果你没有将自动提交设置为true
            con.commit()
            print('111')
        except Exception as e:
            print(e)
            pass


def save_to_mongo(result):
    client = pymongo.MongoClient('192.168.8.211', connect=False)
    db = client['day7']
    try:
        #  加个判断, 如果插入数据失败,再次循环
        if db['day7_tb'].insert(result):
            print("insert into mongo success", result)
            # 查询当前存储的数据条数
            print('当前已存储%d条数据' % db.day7_tb.find().count())
            return True
        else:
            print('插入失败')
            return False
    except:
        print('md5重复')

if __name__ == '__main__':
    pool = Pool(10)
    for i in range(20):
        pool.apply_async(download_url)
    pool.close()
    pool.join()

