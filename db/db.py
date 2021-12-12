import pymysql
import pymysql.cursors
import numpy as np
db = pymysql.connect(host='us-cdbr-east-04.cleardb.com', port=3306, user='b39d8fa6dd08de', passwd='e2b8b154', db='heroku_d34613fc10f0366', charset='utf8')
cursor = db.cursor()
cursor.execute("select * from heroku_d34613fc10f0366.mapa")
row = cursor.fetchone()
list1=[]
while row: #將row輸出成list1陣列
    list1.append(row)
    row = cursor.fetchone()#使row輸出下一行資料列
a = np.array(list1)
c = a.shape[0]
i=1
g='page1,120.609692,24.137992'
k=g.split(',')
page=2
i=5
j=page*5
l=0
l=3/2
print(int(l))
