from flask import Flask, jsonify, session, request
from app.web.violet_comment_functions import Comment
from . import web
from app.web.write_log import send_log
# app = Flask(__name__)


@web.route('/v1/comment/load_comment', methods=['POST'])
def load_comment():
    user_id = session.get('user_id')
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id')
    '''
    测试结果：
    user_id = 1
    item_type = 1
    item_id = 1
    {
    "code": 0,
    "data": [
        {
            "comment_id": 2,
            "content": "测试修改",
            "create_time": "Tue, 19 Nov 2019 23:15:30 GMT",
            "is_liked": false,
            "item_id": 1,
            "item_type": 1,
            "thumbs_up_num": 0,
            "user_id": 1,
            "user_nickname": "胖菊喵喵喵"
        },
        {
            "comment_id": 1,
            "content": "坤坤的wait wait wait太棒了！",
            "create_time": "Tue, 19 Nov 2019 22:45:57 GMT",
            "is_liked": true,
            "item_id": 1,
            "item_type": 1,
            "thumbs_up_num": 1000,
            "user_id": 1,
            "user_nickname": "胖菊喵喵喵"
        }
    ]
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if item_type is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数item_type'
        })
    if item_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数item_id'
        })
    send_log('/v1/comment/load_comment')
    return Comment.comments_to_jsonify(Comment.load_comment(user_id, item_type, item_id))


@web.route('/v1/comment/add_comment', methods=['POST'])
def add_comment():
    user_id = session.get('user_id')
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id')
    content = request.form.get('content')
    '''
    测试结果：
    user_id = 2
    item_type = 2
    item_id = 1
    content = '测试评论'
    {
    "code": 0,
    "Msg": "评论成功,comment_id:3"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if item_type is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数item_type'
        })
    if item_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数item_id'
        })
    if content is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数content'
        })
    send_log('/v1/comment/add_comment')
    return Comment.add_comment(user_id, item_type, item_id, content)


@web.route('/v1/comment/delete_comment', methods=['POST'])
def delete_comment():
    user_id = session.get('user_id')
    comment_id = request.form.get('comment_id')
    '''
    测试结果：
    user_id = 2
    comment_id = 3
    {
    "code": 0,
    "Msg": "删除评论成功"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if comment_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数comment_id'
        })
    send_log('/v1/comment/delete_comment')
    return Comment.delete_comment(user_id, comment_id)


@web.route('/v1/comment/modify_comment', methods=['POST'])
def modify_comment():
    user_id = session.get('user_id')
    comment_id = request.form.get('comment_id')
    content = request.form.get('content')
    '''
    测试结果：
    user_id = 1
    comment_id = 2
    content = '测试修改222'
    {
    "code": 0,
    "Msg": "修改评论成功"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if comment_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数comment_id'
        })
    if content is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数content'
        })
    send_log('/v1/comment/modify_comment')
    return Comment.modify_comment(user_id, comment_id, content)


# if __name__ == '__main__':
#     app.run()
