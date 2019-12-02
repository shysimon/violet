import pymysql
import traceback
from flask import jsonify
from app.web.violet_thumbs_functions import Thumbs

user = 'violet'
pwd = 'violetzjhnb'
host = '45.40.202.216'
port = 3306
database = 'violet'


def get_conn():
    return pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset='utf8')


class Zone(object):
    def __init__(self, zone_id, user_id, create_time, content, item_type, item_id, thumbs_up_num, is_liked):
        self.zone_id = zone_id
        self.user_id = user_id
        self.create_time = create_time
        self.content = content
        self.item_type = item_type
        self.item_id = item_id
        self.thumbs_up_num = thumbs_up_num
        self.is_liked = is_liked

    def to_data(self):
        data = {'zone_id': self.zone_id, 'user_id': self.user_id, 'create_time': self.create_time,
                'content': self.content, 'item_type': self.item_type, 'item_id': self.item_id,
                'thumbs_up_num': self.thumbs_up_num, 'is_liked': self.is_liked}
        if data['user_id'] == 0:  # 表示是系统所有
            data['user_id'] = '动态'
        else:
            conn = get_conn()
            cursor = conn.cursor()
            sql = 'select user_nickname from vuser where user_id = %s'
            cursor.execute(sql, data['user_id'])
            data['user_nickname'] = cursor.fetchall()[0][0]
            cursor.close()
            conn.close()
            return data

    @staticmethod
    def zones_to_jsonify(zones):
        json_data = {}
        try:
            json_data['code'] = 0
            json_data['data'] = []
            for zone in zones:
                json_data['data'].append(zone.to_data())
            return jsonify(json_data)
        except Exception as e:
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data.pop('data')
            json_data['msg'] = e.args
            return jsonify(json_data)

    # TODO
    @staticmethod
    def load_zone(user_id):
        '''
        获取用户动态列表--->最新的动态最先
        SQL嵌套关系：获取当前用户所关注的用户->获取关注的用户所发的动态    *注：用户默认关注自己，由此获取自身所发的动态
        :param user_id: 获取动态的用户id
        :return: 返回一个列表，列表长度为0则表示无动态。列表的每一项为一个字典类型，作为一条动态记录。
        '''
        conn = get_conn()
        cursor = conn.cursor()

        sql = 'select zone_id, user_id, create_time, content, item_type, item_id, thumbs_up_num from vzone \
               where user_id in ( \
                 select user_id from vuser  \
                 where user_id in ( \
                   select to_user_id from vfollow \
                   where user_id = %s) \
                ) \
                order by create_time DESC'
        cursor.execute(sql, [user_id])
        rows = cursor.fetchall()

        zones = []
        for row in rows:
            zone_id = row[0]
            item_type = 6  # vzone类型
            is_liked = Thumbs.query_like(user_id, item_type, zone_id)
            zones.append(Zone(zone_id=zone_id, user_id=row[1], create_time=row[2],
                              content=row[3], item_type=row[4], item_id=row[5],
                              thumbs_up_num=row[6], is_liked=is_liked))

        cursor.close()
        conn.close()

        return zones

    @staticmethod
    def add_zone(user_id, content, item_type, item_id):
        '''
        发一条新的动态
        :param user_id: 发动态的用户id
        :param content: 发动态的内容
        :param item_type: 动态所分享的内容，为0表示无内容
        :param item_id: 动态所分享内容的id
        :return: jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            sql = 'select max(zone_id) from vzone'
            cursor.execute(sql)
            zone_id = cursor.fetchall()[0][0] + 1
            thumbs_up_num = 0

            sql = 'insert into vzone(zone_id, user_id, content, item_type, item_id, thumbs_up_num) \
                   values(%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, [zone_id, user_id, content, item_type, item_id, thumbs_up_num])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '动态发送成功zone_id：' + str(zone_id)
            })
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            return jsonify({
                'code': -1,
                'msg': e.args
            })
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_zone(user_id, zone_id):
        '''
        删除一条动态（保证动态属于用户本身）
        :param user_id:
        :param zone_id: 要删除的动态id
        :return: jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            sql = 'select user_id from vzone where zone_id = %s'
            cursor.execute(sql, [zone_id])
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '动态不存在'
                })
            if str(rows[0][0]) != str(user_id):
                return jsonify({
                    'code': -1,
                    'msg': '该评论属于user_id：' + str(rows[0][0])
                })

            sql = 'select type_id from symbol_table where type_name = %s'
            cursor.execute(sql, ['vzone'])
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '不存在type_name：vzone'
                })
            type_id = rows[0][0]

            sql = 'delete from vthumbsup where item_type = %s and item_id = %s'
            cursor.execute(sql, [type_id, zone_id])
            sql = 'delete from vzone where zone_id = %s'
            cursor.execute(sql, [zone_id])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '删除动态成功'
            })
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            return jsonify({
                'code': -1,
                'msg': e.args
            })
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def modify_zone(user_id, zone_id, content):
        '''
        修改动态内容
        :param user_id:
        :param zone_id: 要修改的动态id
        :param content:  修改后的动态内容
        :return: jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            sql = 'select user_id from vzone where zone_id = %s'
            cursor.execute(sql, [zone_id])
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '动态不存在'
                })
            if str(rows[0][0]) != str(user_id):
                return jsonify({
                    'code': -1,
                    'msg': '该评论属于user_id：' + str(rows[0][0])
                })

            sql = 'update vzone \
                   set content = %s \
                   where zone_id = %s'
            cursor.execute(sql, [content, zone_id])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '动态修改成功'
            })
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            return jsonify({
                'code': -1,
                'msg': e.args
            })
        finally:
            cursor.close()
            conn.close()