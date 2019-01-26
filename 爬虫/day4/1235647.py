import pymssql

server="192.168.8.212"
user="sa"
password="123456"

con=pymssql.connect(server,user,password,"Search")
cursor=con.cursor()

cursor.execute("""
IF OBJECT_ID('table_1', 'U') IS NOT NULL
    DROP TABLE table_1
CREATE TABLE table_1 (
    id VARCHAR (20) NOT NULL,
    title NVARCHAR (4000) NOT NULL,
    author NVARCHAR (4000) NOT NULL,
    patent number VARCHAR (100) NOT NULL,
    page VARCHAR (100) NOT NULL,
    abstract NVARCHAR (max) NOT NULL,
    researchDirection NVARCHAR (4000) NOT NULL,
    data NVARCHAR (25) NOT NULL,
    url VARCHAR (255) NOT NULL,
    md5 VARCHAR (255) NOT NULL,
    PRIMARY KEY(id)
)
""")

cursor.executemany(
    "INSERT INTO table_1 VALUES (%d, %s, %s)",
    [(1, 'John Smith', 'John Doe'),
     (2, 'Jane Doe', 'Joe Dog'),
     (4, 'Mike T.', 'Sarah H.')])
# 你必须调用 commit() 来保持你数据的提交如果你没有将自动提交设置为true
con.commit()
