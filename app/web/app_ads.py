from flask import Flask, jsonify, session, request
from app.web.violet_ads_functions import Ads
from . import web


# app = Flask(__name__)


@web.route('/v1/ads/index_ads', methods=['GET', 'POST'])
def index_ads():
    res = []
    for i in Ads.load_ads_is_used():
        res.append(i.to_data())
    return jsonify({
        'code': 0,
        'data': res
    })

# if __name__ == '__main__':
#     app.run()
