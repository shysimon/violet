from flask import jsonify, session, request
from app.web.violet_thumbs_functions import Thumbs
from . import web
from app.web.write_log import send_log



@web.route('/v1/thumbs/like', methods=['POST'])
def like():
    user_id = session.get('user_id')
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id')

    '''
    user_id = 2
    item_type = 5
    item_id = 2
    测试结果：
    {
    "code": 0,
    "Msg": "点赞成功"
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
    send_log('/v1/thumbs/like')
    return Thumbs.like(user_id, item_type, item_id)


@web.route('/v1/thumbs/dislike', methods=['POST'])
def dislike():
    user_id = session.get('user_id')
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id')

    '''
    user_id = 2
    item_type = 5
    item_id = 2
    测试结果：
    {
    "code": 0,
    "Msg": "取消赞成功"
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
    send_log('/v1/thumbs/dislike')
    return Thumbs.dislike(user_id, item_type, item_id)

# if __name__ == '__main__':
#     app.run()
