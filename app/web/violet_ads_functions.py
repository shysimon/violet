import traceback

import pymysql
from flask import jsonify
import requests

user = 'violet'
pwd = 'violetzjhnb'
host = '45.40.202.216'
port = 3306
database = 'violet'


def get_conn():
    return pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset='utf8')


class Ads(object):
    def __init__(self, ads_id, img_url, target_url, is_used):
        self.ads_id = ads_id
        self.img_url = img_url
        self.target_url = target_url
        self.is_used = is_used

    def to_data(self):
        res = {'ads_id': self.ads_id, 'img_url': self.img_url, 'target_url': self.target_url, 'is_used': self.is_used}
        return res

    @staticmethod
    def load_ads_is_used():
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select ads_id, img_url, target_url, is_used from violet.vads where is_used = 1'
        cursor.execute(sql)
        rows = cursor.fetchall()
        ads = []
        for row in rows:
            ads.append(Ads(row[0], row[1], row[2], row[3]))
        return ads
