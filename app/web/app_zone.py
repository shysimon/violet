from flask import jsonify, session, request
from app.web.violet_zone_functions import Zone
from . import web
from app.web.write_log import send_log



@web.route('/v1/zone/load_zone', methods=['POST'])
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
            'errMsg': '缺少参数user_id'
        })
    send_log('/v1/zone/load_zone')
    return Zone.zones_to_jsonify(Zone.load_zone(user_id))


@web.route('/v1/zone/index_zones', methods=['POST'])
def index_zones():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    send_log('/v1/zone/index_zones')
    return Zone.zones_to_jsonify(Zone.load_zone_top3(user_id))


@web.route('/v1/zone/add_zone', methods=['POST'])
def add_zone():
    user_id = session.get('user_id')
    content = request.form.get('content')
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id')

    '''
    user_id = 3
    content = '测试发送动态内容（无attach）'
    item_type = 0
    item_id = 0
    测试结果：
    {
    "code": 0,
    "Msg": "动态发送成功zone_id：5"
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if content is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数content'
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
    send_log('/v1/zone/add_zone')
    return Zone.add_zone(user_id, content, item_type, item_id)


@web.route('/v1/zone/delete_zone', methods=['POST'])
def delete_zone():
    user_id = session.get('user_id')
    zone_id = request.form.get('zone_id')

    '''
    user_id = 3
    zone_id = 5
    测试结果：
    {
    "code": 0,
    "Msg": "删除动态成功"
    }
    '''

    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if zone_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数zone_id'
        })
    send_log('/v1/zone/delete_zone')
    return Zone.delete_zone(user_id, zone_id)


@web.route('/v1/zone/modify_zone', methods=['POST'])
def modify_zone():
    user_id = session.get('user_id')
    zone_id = request.form.get('zone_id')
    content = request.form.get('content')

    '''
    user_id = 3
    zone_id = 5
    content = '修改后的content'
    测试结果：
    {
    "code": 0,
    "Msg": "动态修改成功"
    }
    '''

    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if zone_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数zone_id'
        })
    if content is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数content'
        })
    send_log('/v1/zone/modify_zone')
    return Zone.modify_zone(user_id, zone_id, content)

# if __name__ == '__main__':
#     app.run()
