import psycopg2
#建立数据库连接
con = psycopg2.connect(database="postgres", user="postgres", password="xialuoke", host="localhost", port="5432")
#调用游标对象
cur = con.cursor()
#用cursor中的execute 使用DDL语句创建一个名为 STUDENT 的表,指定表的字段以及字段类型
cur.execute('''CREATE TABLE anji2019
      (
      CITY        CHAR(50) PRIMARY KEY           NOT NULL,
      SYHY_SW        DOUBLE PRECISION           NOT NULL,
      SYHY_JZ        DOUBLE PRECISION           NOT NULL,
      TRBC_SW        DOUBLE PRECISION           NOT NULL,
      TRBC_JZ        DOUBLE PRECISION           NOT NULL,
      HSTX_SW        DOUBLE PRECISION           NOT NULL,
      HSTX_JZ        DOUBLE PRECISION           NOT NULL,
      GT_SW        DOUBLE PRECISION           NOT NULL,
      GT_JZ        DOUBLE PRECISION           NOT NULL,
      SY_SW        DOUBLE PRECISION           NOT NULL,
      SY_JZ        DOUBLE PRECISION           NOT NULL,
      QHTJ_SW        DOUBLE PRECISION           NOT NULL,
      QHTJ_JZ        DOUBLE PRECISION           NOT NULL);''')

#提交更改，增添或者修改数据只会必须要提交才能生效
con.commit()
con.close()




