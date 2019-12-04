import pymysql
from app.web.violet_thumbs_functions import Thumbs
import traceback
from flask import jsonify
from app.lib.time_output import my_time_to_string

user = 'violet'
pwd = 'violetzjhnb'
host = '45.40.202.216'
port = 3306
database = 'violet'


def get_conn():
    return pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset='utf8')


class Comment(object):
    def __init__(self, comment_id, user_id, item_type, item_id, content, create_time, thumbs_up_num, is_liked):
        self.comment_id = comment_id
        self.user_id = user_id
        self.item_type = item_type
        self.item_id = item_id
        self.content = content
        self.create_time = create_time
        self.thumbs_up_num = thumbs_up_num
        self.is_liked = is_liked

    def to_data(self):
        data = {'comment_id': self.comment_id, 'user_id': self.user_id, 'item_type': self.item_type,
                'item_id': self.item_id, 'content': self.content, 'create_time': my_time_to_string(self.create_time),
                'thumbs_up_num': self.thumbs_up_num, 'is_liked': self.is_liked}
        if data['user_id'] == 0: # 表示是系统所有
            data['user_id'] = '评论'
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
    def comments_to_jsonify(comments):
        json_data = {}
        try:
            json_data['code'] = 0
            json_data['data'] = []
            for comment in comments:
                json_data['data'].append(comment.to_data())
            return jsonify(json_data)
        except Exception as e:
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data.pop('data')
            json_data['msg'] = e.args
            return jsonify(json_data)

    @staticmethod
    def load_comment(user_id, item_type, item_id):
        '''
        获取评论--->最新的评论最先
        :param user_id: 用户id
        :param item_type: 评论所属的种类（歌曲、歌单等）
        :param item_id: 评论的具体对象id
        :return: 返回一个列表与一个int。
        列表长度为0则表示无评论。列表的每一项为一个字典类型，作为一条评论记录。
        '''
        conn = get_conn()
        cursor = conn.cursor()

        sql = 'select comment_id, user_id, item_type, item_id, content, create_time, thumbs_up_num \
               from vcomment \
               where item_type = %s and item_id = %s \
               order by create_time DESC'
        cursor.execute(sql, [item_type, item_id])
        rows = cursor.fetchall()

        comments = []
        for row in rows:
            comment_id = row[0]
            item_type = 5  # 评论
            is_liked = Thumbs.query_like(user_id, item_type, comment_id)
            comments.append(Comment(comment_id=comment_id, user_id=row[1], item_type=row[2],
                                    item_id=row[3], content=row[4], create_time=row[5],
                                    thumbs_up_num=row[6], is_liked=is_liked))
        cursor.close()
        conn.close()

        return comments

    @staticmethod
    def add_comment(user_id, item_type, item_id, content):
        '''
        发送一条评论
        :param user_id: 发送评论的用户id
        :param item_type: 评论的对象（歌曲等）
        :param item_id:  评论对象的id
        :param content:  评论的内容
        :return: jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            sql = 'select max(comment_id) from vcomment'
            cursor.execute(sql)
            comment_id = cursor.fetchall()[0][0] + 1
            thumbs_up_num = 0

            sql = 'insert into vcomment(comment_id, user_id, item_type, item_id, content, thumbs_up_num) \
                   values(%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, [comment_id, user_id, item_type, item_id, content, thumbs_up_num])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '评论成功,comment_id:' + str(comment_id)
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
    def delete_comment(user_id, comment_id):
        '''
        :param user_id:
        :param comment_id:
        :return:
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            sql = 'select user_id from vcomment where comment_id = %s'
            cursor.execute(sql, [comment_id])
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '评论不存在'
                })
            if str(rows[0][0]) != str(user_id):
                return jsonify({
                    'code': -1,
                    'msg': '该评论属于user_id：' + str(rows[0][0])
                })

            sql = 'select type_id from symbol_table where type_name = %s'
            cursor.execute(sql, ['vcomment'])
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '不存在type_name：vcomment'
                })
            type_id = rows[0][0]

            sql = 'delete from vthumbsup where item_type = %s and item_id = %s'
            cursor.execute(sql, [type_id, comment_id])
            sql = 'delete from vcomment where comment_id = %s'
            cursor.execute(sql, [comment_id])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '删除评论成功'
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
    def modify_comment(user_id, comment_id, content):
        '''
        修改评论内容
        :param comment_id: 要修改的评论id
        :param content: 修改后的评论内容
        :return: jsonify
        '''
        conn = get_conn()
        cursor = conn.cursor()

        try:
            sql = 'select user_id from vcomment where comment_id = %s'
            cursor.execute(sql, [comment_id])
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '评论不存在'
                })
            if str(rows[0][0]) != str(user_id):
                return jsonify({
                    'code': -1,
                    'msg': '该评论属于user_id：' + str(rows[0][0])
                })

            sql = 'update vcomment set content = %s where comment_id = %s'
            cursor.execute(sql, [content, comment_id])
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '修改评论成功'
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