from flask import Flask, jsonify, session
from app.web.violet_thumbs_functions import Thumbs
from . import web

# app = Flask(__name__)


@web.route('/v1/thumbs/like', methods=['POST'])
def like():
    user_id = session.get('user_id')
    item_type = None
    item_id = None

    '''
    user_id = 2
    item_type = 5
    item_id = 2
    测试结果：
    {
    "code": 0,
    "msg": "点赞成功"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })
    if item_type is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数item_type'
        })
    if item_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数item_id'
        })

    return Thumbs.like(user_id, item_type, item_id)


@web.route('/v1/thumbs/dislike', methods=['POST'])
def dislike():
    user_id = session.get('user_id')
    item_type = None
    item_id = None

    '''
    user_id = 2
    item_type = 5
    item_id = 2
    测试结果：
    {
    "code": 0,
    "msg": "取消赞成功"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })
    if item_type is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数item_type'
        })
    if item_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数item_id'
        })

    return Thumbs.dislike(user_id, item_type, item_id)


# if __name__ == '__main__':
#     app.run()
