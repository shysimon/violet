import pymysql
from datetime import datetime
import traceback
from flask import jsonify
from app.lib.time_output import my_time_to_string


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


class Group(object):
    def __init__(self, group_id, group_name, create_time, info, thumbs_up_num, follow_num, user_id):
        self.group_id = group_id
        self.group_name = group_name
        self.create_time = create_time
        self.info = info
        self.thumbs_up_num = thumbs_up_num
        self.follow_num = follow_num
        self.user_id = user_id

    @staticmethod
    def load_group():
        '''
        加载所有圈子
        圈子按其关注人数从大到小排序
        :return:返回一个json格式数据，格式如下：
        {
          'code'： 函数执行结果（0表示成功，-1表示失败）
          'data': [{ group_id: 圈子id，
                group_name: 圈子名称
                create_time: 创建时间
                info: 圈子简介
                thumbs_up_num: 圈子点赞数
                follow_num: 圈子关注人数
                user_id: 圈子创建者id]}
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = ['failed to load group']
        try:
            sql = 'select * from vgroup order by follow_num desc'
            cursor.execute(sql)
            result = cursor.fetchall()
            for i in result:
                i['create_time'] = my_time_to_string(i['create_time'])
            json_data['code'] = 0
            json_data['data'] = result
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            print(e.args)
            print(traceback.format_exc())
            json_data['msg'] = e.args
            return jsonify(json_data)
        finally:
            conn.close()
            cursor.close()

    @staticmethod
    def add_group(user_id, group_name, info, thumbs_up_num=0, follow_num=0):
        '''
        创建圈子
        :param user_id: 创建者id
        :param group_name: 圈子名称
        :param info: 圈子简介
        :param thumbs_up_num: 点赞数（默认为0）
        :param follow_num: 关注人数（默认为0）
        :return:返回json格式数据，格式如下：
        { 'code':函数执行结果（0为成功，-1为失败）
          'data':[] (返回空列表)
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = ['failed to add group']
        try:
            sql = 'select * from vgroup where group_name = \'' + group_name + '\''
            if cursor.execute(sql) > 0:
                print('the group name is occupied')
                json_data['data'] = '该圈子名已被占用'
                return json_data
            sql = 'insert into vgroup' \
                  '(user_id,group_name,create_time,info,thumbs_up_num,follow_num)' \
                  ' values' \
                  ' (%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, [user_id, group_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), info, thumbs_up_num,
                                 follow_num])
            json_data['code'] = 0
            json_data['data'] = '添加圈子成功'
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['data'] = e.args
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def delete_group(group_id, user_id):
        '''
        删除指定的圈子
        :param group_id: 要删除的圈子的id
        :return:返回json格式数据，格式如下：
        { 'code':函数执行结果（0为成功，-1为失败）
          'data':[] (返回空列表)
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = ['failed to delete group']
        try:
            sql = 'select user_id from violet.vgroup where group_id  = %s'
            cursor.execute(sql, [group_id])
            rows = cursor.fetchall()
            if str(rows[0][0]) != user_id:
                json_data['data'].append('歌单属于userid: ' + str(rows[0][0]))
                return jsonify(json_data)
            sql = 'delete from vpost where group_id = %s'
            cursor.execute(sql, [group_id])
            sql = 'delete from vgroup where group_id  = %s'
            cursor.execute(sql, [group_id])
            json_data['code'] = 0
            json_data['data'] = '删除圈子成功'
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['data'] = e.args
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def invite_user(friend_id, group_id):
        '''
        邀请好友加入圈子
        （暂时设计成：不需要询问好友，直接拉入圈子）
        :param friend_id: 好友id
        :param group_id: 圈子id
        :return:返回json格式数据，格式如下：
        { 'code': 函数执行情况(0为成功，-1为失败)
          'data': [] (返回空列表)
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = ['failed to invite friend']
        try:
            sql = 'select * from user_group where user_id = %s and group_id = %s'
            if cursor.execute(sql, [friend_id, group_id]) > 0:
                print('your friend has already followed this group')
                json_data['data'] = '好友已在该圈子中'
                return json_data
            sql = 'insert into user_group(user_id,group_id) values (%s, %s)'
            cursor.execute(sql, [friend_id, group_id])
            json_data['code'] = 0
            json_data['data'] = '邀请好友成功'
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['data'] = e.args
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

    @staticmethod
    def search_group(keyword):
        '''
        搜索圈子
        暂时只支持按名称搜索
        :param keyword: 圈子名称
        :return:返回json格式数据，格式如下：
        { 'code':返回函数执行情况（0为成功，-1为失败）
          'data':[{
                'group_id': 圈子id
                'gruop_name': 圈子名称
                'create_time': 创建时间
                'info': 圈子简介
                'thumbs_up_num': 圈子点赞数
                'follow_num': 关注人数
                'user_id': 创建者id}]
        }
        '''
        cursor, conn = get_connection()
        json_data = dict()
        json_data['code'] = -1
        json_data['data'] = ['failed to search group']
        try:
            sql = 'select * from vgroup where group_name like "%' + str(keyword) + '%" order by follow_num desc'
            cursor.execute(sql)
            result = cursor.fetchall()
            json_data['code'] = 0
            json_data['data'] = result
            print('success!')
            return jsonify(json_data)
        except BaseException as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['data'] = e.args
            return jsonify(json_data)
        finally:
            conn.commit()
            conn.close()
            cursor.close()

# if __name__ == '__main__':
#     print('hello world')
# data = search_group('group')
# print(data)
# print('hello world!')
# Group.search_group(group)
