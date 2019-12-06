from flask import Flask, session, jsonify, request
from app.web.group_recommend_system import GroupRecommendSystem, group_to_jsonify
from . import web


# app = Flask(__name__)


# @web.route('/')
# def hello_world():
#     return 'Hello World!'


@web.route('/v1/recommend/group', methods=['POST', 'GET'])
def recommend_group():
    user_id = session.get('user_id')
    beta = request.form.get('beta')
    '''
       user_id = 1;
       beta = None
       测试结果：
       {
          "code": 0,
          "data": [
            {
              "create_time": "Tue, 19 Nov 2019 16:52:54 GMT",
              "follow_num": 250,
              "group_id": 1,
              "group_name": "菜徐坤后援会",
              "info": "鲲鲲最棒棒",
              "similarity": 0.9265986323710904,
              "thumbs_up_num": 999,
              "user_id": 1
            },
            {
              "create_time": "Wed, 20 Nov 2019 11:24:08 GMT",
              "follow_num": 0,
              "group_id": 8,
              "group_name": "groupgroupgroup",
              "info": "infoinfoinfo",
              "similarity": 0.5999999999999999,
              "thumbs_up_num": 0,
              "user_id": 1
            }
          ]
        }
       '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })

    recommender = GroupRecommendSystem()

    if beta is None:    # 采用默认的权重β= 0.6
        return group_to_jsonify(recommender.recommend_group(user_id))
    else:
        return group_to_jsonify(recommender.recommend_group(user_id, beta))


# if __name__ == '__main__':
#     app.run()