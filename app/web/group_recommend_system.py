import pymysql
import traceback
from flask import jsonify


def get_connection():
    '''
    获取数据库连接
    :return:
    '''
    user = 'violet'
    pwd = 'violetzjhnb'
    host = '45.40.202.216'
    port = 3306
    database = 'violet'
    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset='utf8')

    return conn


def user_to_data(user_id, sim):
    conn = get_connection()
    cursor = conn.cursor()

    sql = 'select user_nickname, password, gender, birthday, motto, thumbs_up_num, user_type, info, email from vuser where user_id = %s'
    cursor.execute(sql, [user_id])
    row = cursor.fetchall()[0]

    data = {'user_id': user_id, 'user_nickname': row[0], 'password': row[1], 'gender': row[2], 'birthday': row[3],
            'motto': row[4], 'thumbs_up_num': row[5], 'user_type': row[6], 'info': row[7], 'email': row[8],
            'similarity': sim}

    return data


def user_to_jsonify(users):
    json_data = {}
    try:
        json_data['code'] = 0
        json_data['data'] = []
        for user in users:
            user_id = user[0]
            if user_id == 0:
                continue
            sim = user[1]
            user_data = user_to_data(user_id, sim)
            json_data['data'].append(user_data)
        return jsonify(json_data)
    except Exception as e:
        print(e.args)
        print(traceback.format_exc())
        json_data['code'] = -1
        json_data.pop('data')
        json_data['errMsg'] = e.args
        return jsonify(json_data)


class UserRecommendSystem(object):
    @staticmethod
    def load_liked_items():
        '''
        根据数据库查找每一个用户所点赞的内容
        :return:
        '''
        conn = get_connection()
        cursor = conn.cursor()

        sql = 'select distinct user_id from vthumbsup'
        cursor.execute(sql)
        user_ids = cursor.fetchall()

        user_items = {}

        for user_id in user_ids:
            user_id = user_id[0]
            sql = 'select item_type, item_id from vthumbsup where user_id = %s'
            cursor.execute(sql, [user_id])
            rows = cursor.fetchall()

            list_items = []
            for row in rows:
                item = LikedItem(user_id, row[0], row[1])
                list_items.append(item)

            user_items[user_id] = list_items

        return user_items