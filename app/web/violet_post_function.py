import pymysql
from datetime import datetime
from flask import jsonify
import traceback

from app.lib.time_output import my_time_to_string
from app.web.violet_thumbs_functions import Thumbs


def get_connection():
    '''
    建立mysql连接
    :return:
    cursor：返回执行sql语句的光标对象
    conn：返回连接
    '''
    conn = pymysql.connect(
        host='45.40.202.216',
        port=3306,
        user='violet',
        password='violetzjhnb',
        database='violet',
        charset='utf8'
    )
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    return cursor, conn


class Post(object):
    def __init__(self, post_id, group_id, user_id, post_title, content, create_time, recent_time, thumbs_up_num,
                 is_liked):
        self.post_id = post_id
        self.group_id = group_id
        self.user_id = user_id
        self.post_title = post_title
        self.content = content
        self.create_time = create_time
        self.recent_time = recent_time
        self.thumbs_up_num = thumbs_up_num
        self.is_liked = is_liked

    @staticmethod
    def load_post(group_id, user_id):
        '''
        加载指定圈子下所有帖子
        帖子按其最新评论时间排序
        :param group_id:
        :return:返回json格式数据，格式如下:
        { 'code': 返回函数执行情况（0表示成功，-1表示失败）
          'data':[{
    `           'post_id': 帖子id
                'group_id': 隶属圈子id
                'user_id': 帖子创建者id
                'post_title': 帖子标题
                'content': 帖子内容
                'create_time': 创建时间
                'recent_time': 最新评论时间
                'thumbs_up_num': 点赞数
          }]
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = []
        try:
            sql = 'select * from vpost where group_id = %s order by recent_time desc '
            cursor.execute(sql, [group_id])
            result = cursor.fetchall()
            json_data['data'] = []
            for post in result:
                json_data['data'].append(Post.result_to_data(post, cursor, user_id))
            json_data['code'] = 0
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            json_data['data'] = e.args
            print(e.args)
            print(traceback.format_exc())
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def add_post(group_id, user_id, post_title, content, thumbs_up_num=0):
        '''
        在指定圈子下发帖

        :param group_id: 圈子id
        :param user_id:  发帖人id
        :param post_title: 帖子标题
        :param content: 帖子内容
        :param thumbs_up_num: 点赞数
        :return: 返回json格式数据，格式如下：
        { 'code':返回函数执行情况（0表示成功，-1表示失败）
          'data':[] (返回空列表)
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = []
        try:
            dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = 'insert into vpost' \
                  '(group_id, user_id, post_title, content, create_time, recent_time, thumbs_up_num)' \
                  'values ' \
                  '(%s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, [group_id, user_id, post_title, content, dt, dt, thumbs_up_num])
            json_data['code'] = 0
            json_data['data'] = '添加帖子成功'
            print('success')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            json_data['data'] = e.args
            print(e.args)
            print(traceback.format_exc())
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def delete_post(post_id):
        '''
        删帖功能
        :param post_id: 帖子id
        :return: 返回json格式数据，格式如下：
        { 'code':返回函数执行情况（0表示成功，-1表示失败）
          'data':[] (返回空列表)
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = []
        try:
            sql = 'delete from vcomment where item_type = %s and item_id = %s'
            cursor.execute(sql, [4, post_id])

            sql = 'delete from vpost where post_id = %s'
            cursor.execute(sql, [post_id])
            json_data['code'] = 0
            json_data['data'] = '删除帖子成功'
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            json_data['data'] = e.args
            print(e.args)
            print(traceback.format_exc())
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def modify_post(post_id, new_content):
        '''
        修改帖子功能
        （目前仅能修改内容）
        :param post_id: 帖子id
        :param new_content: 修改内容
        :return: 返回json格式数据，格式如下：
        { 'code':返回函数执行情况（0表示成功，-1表示失败）
          'data':[] (返回空列表)
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = []
        try:
            sql = 'update vpost set content = %s where post_id = %s'
            cursor.execute(sql, [new_content, post_id])
            json_data['code'] = 0
            json_data['data'] = '修改帖子成功'
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            json_data['data'] = e.args
            print(e.args)
            print(traceback.format_exc())
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def search_post(keyword, group_id, user_id):
        '''
        在指定圈子下搜索帖子
        :param keyword: 帖子标题
        :param group_id: 圈子id
        :return: 返回json格式数据，格式如下：
        { 'code': 返回函数执行情况（0表示成功，-1表示失败）
          'data':[{
    `           'post_id': 帖子id
                'group_id': 隶属圈子id
                'user_id': 帖子创建者id
                'post_title': 帖子标题
                'content': 帖子内容
                'create_time': 创建时间
                'recent_time': 最新评论时间
                'thumbs_up_num': 点赞数
          }]
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = []
        try:
            sql = 'select * from vpost where group_id = \'' + group_id + '\' and post_title like \'%' + keyword + '%\''
            cursor.execute(sql)
            result = cursor.fetchall()
            json_data['data'] = []
            for post in result:
                json_data['data'].append(Post.result_to_data(post, cursor, user_id))
            json_data['code'] = 0
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            json_data.pop('data')
            json_data['errMsg'] = e.args
            print(e.args)
            print(traceback.format_exc())
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def result_to_data(post, cursor, user_id):
        sql = 'select count(*) from vcomment where item_type = 4 and item_id = %s'
        cursor.execute(sql, post['post_id'])
        rows = cursor.fetchall()
        count = rows[0]['count(*)']
        post['comment_count'] = count

        post_id = post['post_id']
        is_liked = Thumbs.query_like(user_id, 4, post_id)
        post['is_liked'] = is_liked
        post['create_time'] = my_time_to_string(post['create_time'])
        post['recent_time'] = my_time_to_string(post['recent_time'])
        sql = 'select user_nickname from vuser where user_id = %s'
        cursor.execute(sql, post['user_id'])
        post['owner_nickname'] = cursor.fetchall()[0]['user_nickname']
        return post


if __name__ == '__main__':
    data = Post.load_post(8)
    print(data)
