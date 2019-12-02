from flask import Flask, jsonify, session
from app.web.violet_zone_functions import Zone

app = Flask(__name__)


@app.route('/v1/zone/load_zone', methods=['POST'])
def load_zone():
    user_id = session.get('user_id')

    '''
    user_id = 1
    测试结果：
    {
    "code": 0,
    "data": [
        {
            "content": "user6 zone3",
            "create_time": "Tue, 19 Nov 2019 21:43:51 GMT",
            "is_liked": false,
            "item_id": 0,
            "item_type": 0,
            "thumbs_up_num": 3,
            "user_id": 6,
            "user_nickname": "用户4",
            "zone_id": 3
        },
        {
            "content": "user2 zone2",
            "create_time": "Tue, 19 Nov 2019 21:43:29 GMT",
            "is_liked": true,
            "item_id": 0,
            "item_type": 0,
            "thumbs_up_num": 13,
            "user_id": 2,
            "user_nickname": "ikun永相随",
            "zone_id": 2
        },
        {
            "content": "user1 zone1",
            "create_time": "Tue, 19 Nov 2019 21:43:06 GMT",
            "is_liked": false,
            "item_id": 0,
            "item_type": 0,
            "thumbs_up_num": 11,
            "user_id": 1,
            "user_nickname": "胖菊喵喵喵",
            "zone_id": 1
        }
    ]
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })

    return Zone.zones_to_jsonify(Zone.load_zone(user_id))


@app.route('/v1/zone/add_zone', methods=['POST'])
def add_zone():
    user_id = session.get('user_id')
    content = None
    item_type = None
    item_id = None

    '''
    user_id = 3
    content = '测试发送动态内容（无attach）'
    item_type = 0
    item_id = 0
    测试结果：
    {
    "code": 0,
    "msg": "动态发送成功zone_id：5"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })
    if content is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数content'
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

    return Zone.add_zone(user_id, content, item_type, item_id)


@app.route('/v1/zone/delete_zone', methods=['POST'])
def delete_zone():
    user_id = session.get('user_id')
    zone_id = None

    '''
    user_id = 3
    zone_id = 5
    测试结果：
    {
    "code": 0,
    "msg": "删除动态成功"
    }
    '''

    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })
    if zone_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数zone_id'
        })

    return Zone.delete_zone(user_id, zone_id)


@app.route('/v1/zone/modify_zone', methods=['POST'])
def modify_zone():
    user_id = session.get('user_id')
    zone_id = None
    content = None

    '''
    user_id = 3
    zone_id = 5
    content = '修改后的content'
    测试结果：
    {
    "code": 0,
    "msg": "动态修改成功"
    }
    '''

    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })
    if zone_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数zone_id'
        })
    if content is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数content'
        })

    return Zone.modify_zone(user_id, zone_id, content)


if __name__ == '__main__':
    app.run()
