import pyodbc
import json
from math import radians, cos, sin, asin, sqrt
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Mylinebot;Trusted_Connection=yes')
cursor = cnxn.cursor()
cursor.execute("select [房東姓名],[房東電話],[租屋住址],[房租],[坪數],[經度E],[緯度N] from [dbo].[MAPA] UNION Select [房東姓名],[房東電話],[租屋住址],[房租],[坪數],[經度E],[緯度N] from [dbo].[MAPB]")
row = cursor.fetchone() # row type是 pyodbc.row 不能直接使用

def haversine(lon1, lat1, lon2, lat2):#計算距離的函式,緯度lat,經度lon
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

list1=[]
while row:#符合要求的資料傳入list1
    if haversine(24.145352478289034, 120.61246882666099,row[6],row[5])<0.5:#兩點距離若小於0.2km
        list1.append(row)
    row = cursor.fetchone()#使row輸出下一行資料列
print(list1)

'''
list1=[]
while row: #將row輸出成list1陣列
    list1.append(row)
    row = cursor.fetchone()#使row輸出下一行資料列
'''
'''
jsonstr = row[4] # 將第1筆資料取出為字串
myjson = json.loads(jsonstr) # 將處理過後文字轉成json格式
print(myjson[0].get("緯度N")) #使用json資料
'''
#24.145352478289034, 120.61246882666099
'''
list2=[]
for j in list1:
    if haversine(24.145352478289034, 120.61246882666099,j[6],j[5])<0.2:#兩點距離若小於0.2km
        list2.append(j)
print(list2)
'''