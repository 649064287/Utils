import pandas as pd
import psycopg2

def insert_tablemany(list_rows):
    '''将多条数据插入'''
    sql = "INSERT INTO anji2019 values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # 建立数据库连接
    con = psycopg2.connect(database="postgres", user="postgres", password="xialuoke", host="localhost", port="5432")
    # 调用游标对象
    cur = con.cursor()
    try:
        cur.executemany(sql, list_rows)
        con.commit()
        con.close()
    except:
        print("fail!")
        con.rollback()

#2020
# df = pd.read_excel(r"C:\Users\64906\Desktop\安吉县2019、2020生态系统生产总值汇总.xlsx", 'Sheet1', header=0)
#2019
df = pd.read_excel(r"C:\Users\64906\Desktop\安吉县2019、2020生态系统生产总值汇总.xlsx", 'Sheet2', header=0)
data = []
for index,row in df[2:22].iterrows():
    list = []
    for r in row.values:
        list.append(r)
    data.append(tuple(list))
insert_tablemany(data)





