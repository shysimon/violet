from flask import Flask

import pymysql

# 打开数据库连接
from app import create_app

app = create_app()
# db = pymysql.connect(host="", user="violet", password="violetzjhnb",  port=3306, database="violet", charset='utf8')
#
# # 使用 cursor() 方法创建一个游标对象 cursor
# cursor = db.cursor()
#
# # 使用 execute()  方法执行 SQL 查询
# cursor.execute("SELECT VERSION()")
#
# # 使用 fetchone() 方法获取单条数据.
# data = cursor.fetchone()
#
# print("Database version : %s " % data)
# 1
# # 关闭数据库连接
# db.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=app.config['DEBUG'])
