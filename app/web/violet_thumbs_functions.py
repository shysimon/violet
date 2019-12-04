from flask import jsonify
import traceback
import pymysql

user = 'violet'
pwd = 'violetzjhnb'
host = '45.40.202.216'
port = 3306
database = 'violet'


def get_conn():
    return pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset='utf8')


class Thumbs(object):
    def __init__(self, user_id, item_type, item_id):
        self.user_id = user_id
        self.item_type = item_type
        self.item_id = item_id

    def to_data(self):
        data = {'user_id': self.user_id, 'item_type': self.item_type, 'item_id': self.item_id}
        if data['user_id'] == 0:  # 表示是系统所有
            data['user_id'] = '点赞'
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
    def query_like(user_id, item_type, item_id):
        '''
        判断用户是否对某个内容点赞
        :param user_id: 用户id
        :param item_type: 内容种类
        :param item_id: 内容对象id
        :return:
        返回值为True表示存在点赞记录
        返回值为False表示不存在点赞记录
        '''
        conn = pymysql.connect(host=host, port=port, user=user, password=pwd, db=database, charset='utf8')
        cursor = conn.cursor()

        sql = 'select count(*) \
               from vthumbsup \
               where user_id = %s and item_type = %s and item_id = %s'
        cursor.execute(sql, [user_id, item_type, item_id])
        cnt = cursor.fetchall()[0][0]

        cursor.close()
        conn.close()

        if cnt == 0:
            return False
        else:
            return True

    @staticmethod
    def like(user_id, item_type, item_id):
        item_type = int(item_type)
        '''
        点赞
        :param user_id: 点赞的用户id
        :param item_type: 点赞的内容种类（歌曲等）
        :param item_id: 点赞的对象id
        :return: jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            is_liked = Thumbs.query_like(user_id, item_type, item_id)
            if is_liked == True:
                return jsonify({
                    'code': -1,
                    'msg': '已存在点赞记录'
                })
            if item_type == 1:
                sql = 'update vsong set thumbs_up_num = thumbs_up_num + 1 where song_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 2:
                sql = 'update vsongsheet set thumbs_up_num = thumbs_up_num + 1 where sheet_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 3:
                sql = 'update vsinger set thumbs_up_num = thumbs_up_num + 1 where singer_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 4:
                sql = 'update vpost set thumbs_up_num = thumbs_up_num + 1 where post_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 5:
                sql = 'update vcomment set thumbs_up_num = thumbs_up_num + 1 where comment_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 6:
                sql = 'update vzone set thumbs_up_num = thumbs_up_num + 1 where zone_id = %s'
                cursor.execute(sql, item_id)
            else:
                print(type(item_type))

            sql = 'insert into vthumbsup(user_id, item_type, item_id) \
                   values(%s, %s, %s)'
            cursor.execute(sql, [user_id, item_type, item_id])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '点赞成功'
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
    def dislike(user_id, item_type, item_id):
        item_type = int(item_type)
        '''
        取消赞
        :param user_id: 取消赞的用户id
        :param item_type: 取消赞的内容种类（歌曲等）
        :param item_id: 取消赞的对象id
        :return:jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            is_liked = Thumbs.query_like(user_id, item_type, item_id)

            if is_liked == False:
                return jsonify({
                    'code': -1,
                    'msg': '不存在点赞记录'
                })

            if item_type == 1:
                sql = 'update vsong set thumbs_up_num = thumbs_up_num - 1 where song_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 2:
                sql = 'update vsongsheet set thumbs_up_num = thumbs_up_num - 1 where sheet_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 3:
                sql = 'update vsinger set thumbs_up_num = thumbs_up_num - 1 where singer_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 4:
                sql = 'update vpost set thumbs_up_num = thumbs_up_num - 1 where post_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 5:
                sql = 'update vcomment set thumbs_up_num = thumbs_up_num - 1 where comment_id = %s'
                cursor.execute(sql, item_id)
            elif item_type == 6:
                sql = 'update vzone set thumbs_up_num = thumbs_up_num - 1 where zone_id = %s'
                cursor.execute(sql, item_id)

            sql = 'delete from vthumbsup \
                   where user_id = %s and item_type = %s and item_id = %s'
            cursor.execute(sql, [user_id, item_type, item_id])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '取消赞成功'
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
