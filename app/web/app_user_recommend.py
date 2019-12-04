from flask import Flask, jsonify, session, request
from app.web.user_recommend_system import UserRecommendSystem, user_to_jsonify
from . import web

# app = Flask(__name__)


@web.route('/v1/recommend/user', methods=['POST'])
def recommend_user():
    user_id = session.get('user_id')
    beta = request.form.get('beta')

    '''
    user_id = 1
    beta = None
    测试结果：
    {
    "code": 0,
    "data": [
        {
            "birthday": "Tue, 19 Nov 2019 00:00:00 GMT",
            "email": "100863@qq.com",
            "gender": 1,
            "info": null,
            "motto": "love kunkun",
            "password": "lovekun",
            "similarity": 0.9080880229039762,   # 与要推荐用户的相似度
            "thumbs_up_num": 0,
            "user_id": 2,
            "user_nickname": "ikun永相随",
            "user_type": 0
        },
        {
            "birthday": "Sat, 16 Nov 2019 00:00:00 GMT",
            "email": "100866@qq.com",
            "gender": 0,
            "info": null,
            "motto": "motto3",
            "password": "user",
            "similarity": 0.8309401076758504,
            "thumbs_up_num": 3,
            "user_id": 5,
            "user_nickname": "用户3",
            "user_type": 0
        },
        {
            "birthday": "Mon, 18 Nov 2019 00:00:00 GMT",
            "email": "100864@qq.com",
            "gender": 0,
            "info": null,
            "motto": "motto1",
            "password": "user",
            "similarity": 0.5693653333635273,
            "thumbs_up_num": 1,
            "user_id": 3,
            "user_nickname": "用户1",
            "user_type": 0
        },
        {
            "birthday": "Sun, 17 Nov 2019 00:00:00 GMT",
            "email": "100865@qq.com",
            "gender": 1,
            "info": null,
            "motto": "motto2",
            "password": "user",
            "similarity": 0.10606601717798211,
            "thumbs_up_num": 2,
            "user_id": 4,
            "user_nickname": "用户2",
            "user_type": 0
        }
    ]
    }
    '''
    if user_id is None:
        return jsonify({
            'code': -1,
            'msg': '缺少参数user_id'
        })

    recommender = UserRecommendSystem()

    if beta is None:    # 采用默认的权重β= 0.6
        return user_to_jsonify(recommender.recommend_user(user_id))
    else:
        return user_to_jsonify(recommender.recommend_user(user_id, beta))


# if __name__ == '__main__':
#     app.run()