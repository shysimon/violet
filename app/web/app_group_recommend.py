from flask import Flask, jsonify, request
from app.web.group_recommend_system import GroupRecommendSystem, user_to_jsonify
from . import web


# app = Flask(__name__)


# @web.route('/')
# def hello_world():
#     return 'Hello World!'


@web.route('/v1/recommend/group', methods=['POST'])
def recommend_group():
    # user_id = session.get('user_id')
    user_id = 1
    beta = request.form.get('beta')

    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })

    recommender = GroupRecommendSystem

    if beta is None:    # 采用默认的权重β= 0.6
        return user_to_jsonify(recommender.recommend_group(user_id))
    else:
        return user_to_jsonify(recommender.recommend_group(user_id, beta))


# if __name__ == '__main__':
#     app.run()aa