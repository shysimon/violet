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


class SongSheet(object):
    def __init__(self, sheet_id, sheet_name, owner, sheet_img, play_times, info, thumbs_up_num, follow_num):
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.owner = owner
        self.sheet_img = sheet_img
        self.play_times = play_times
        self.info = info
        self.thumbs_up_num = thumbs_up_num
        self.follow_num = follow_num

    def to_data(self, user_id):
        conn = get_conn()
        cursor = conn.cursor()
        res = {'sheet_id': self.sheet_id, 'sheet_name': self.sheet_name, 'owner': self.owner,
               'sheet_img': self.sheet_img, 'play_times': self.play_times, 'info': self.info,
               'thumbs_up_num': self.thumbs_up_num, 'follow_num': self.follow_num}
        sql = 'select count(*) from vcomment where item_type = 2 and item_id = %s'
        cursor.execute(sql, res['sheet_id'])
        res['comment_count'] = cursor.fetchall()[0][0]
        if res['owner'] == 0:
            res['owner'] = '专辑'
        else:
            sql = 'select user_nickname from vuser where user_id = %s'
            cursor.execute(sql, res['owner'])
            res['owner'] = cursor.fetchall()[0][0]
        sql = "select * from user_songsheet where user_id = %s and sheet_id = %s"
        cursor.execute(sql, (user_id, self.sheet_id))
        if len(cursor.fetchall()) == 0:
            res['is_followed'] = False
        else:
            res['is_followed'] = True
        sql = "select * from vthumbsup where user_id = %s and item_id = %s and item_type = 2"
        cursor.execute(sql, (user_id, self.sheet_id))
        if len(cursor.fetchall()) == 0:
            res['is_thumbs_up'] = False
        else:
            res['is_thumbs_up'] = True
        cursor.close()
        conn.close()
        return res

    @staticmethod
    def query_by_owner(owner):
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select sheet_id, sheet_name, owner, sheet_img, play_times, info, thumbs_up_num, follow_num from vsongsheet where owner = %s'
        cursor.execute(sql, owner)
        rows = cursor.fetchall()
        song_sheets = []
        for row in rows:
            song_sheets.append(SongSheet(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('SongSheet.query_by_owner() success')
        return song_sheets

    @staticmethod
    def query_by_name(name):
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select sheet_id, sheet_name, owner, sheet_img, play_times, info, thumbs_up_num, follow_num from vsongsheet where sheet_name like %s'
        cursor.execute(sql, '%' + name + '%')
        rows = cursor.fetchall()
        song_sheets = []
        for row in rows:
            song_sheets.append(SongSheet(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('SongSheet.query_by_name() success')
        return song_sheets

    @staticmethod
    def query_all():
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select sheet_id, sheet_name, owner, sheet_img, play_times, info, thumbs_up_num, follow_num from vsongsheet'
        cursor.execute(sql)
        rows = cursor.fetchall()
        song_sheets = []
        for row in rows:
            song_sheets.append(SongSheet(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('SongSheet.query_all() success')
        return song_sheets

    @staticmethod
    def query_by_user(user_id):
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select sheet_id from user_songsheet where user_id = %s'
        cursor.execute(sql, user_id)
        rows = cursor.fetchall()
        sheet_ids = []
        for row in rows:
            sheet_ids.append(row[0])
        sql = 'select sheet_id, sheet_name, owner, sheet_img, play_times, info, thumbs_up_num, follow_num from vsongsheet where sheet_id = %s'
        song_sheets = []
        for i in sheet_ids:
            cursor.execute(sql, i)
            row = cursor.fetchall()[0]
            song_sheets.append(SongSheet(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('SongSheet.query_by_user() success')
        return song_sheets

    @staticmethod
    def create_sheet(sheet_name, owner, sheet_img=None):
        json_data = dict()
        conn = get_conn()
        cursor = conn.cursor()
        try:
            sql = "insert into vsongsheet(sheet_name, owner, sheet_img, play_times, info, thumbs_up_num, follow_num) values(%s,%s,%s,0,null,0,1)"
            cursor.execute(sql, (sheet_name, owner, sheet_img))
            print(cursor.lastrowid)
            sheet_id = cursor.lastrowid
            sql = "insert into user_songsheet(sheet_id, user_id) values(%s,%s)"
            cursor.execute(sql, (sheet_id, owner))
            conn.commit()
            json_data['code'] = 0
            json_data['msg'] = '添加歌单成功,sheet_id:' + str(sheet_id)
            return jsonify(json_data)
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data['msg'] = e.args
            return jsonify(json_data)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_sheet(sheet_id, owner):
        json_data = dict()
        conn = get_conn()
        cursor = conn.cursor()
        try:
            sql = 'select owner from vsongsheet where sheet_id = %s'
            cursor.execute(sql, sheet_id)
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '歌单不存在'
                })
            if str(rows[0][0]) != owner:
                return jsonify({
                    'code': -1,
                    'msg': '歌单属于userid: ' + str(rows[0][0])
                })
            sql = 'select type_id from symbol_table where type_name= %s'
            cursor.execute(sql, 'vsongsheet')
            type_id = cursor.fetchall()[0][0]
            sql = 'delete from user_songsheet where sheet_id = %s'
            cursor.execute(sql, sheet_id)
            sql = 'delete from song_songsheet where sheet_id = %s'
            cursor.execute(sql, sheet_id)
            sql = 'delete from vcomment where item_id = %s and item_type = %s'
            cursor.execute(sql, (sheet_id, type_id))
            sql = 'delete from vthumbsup where item_id = %s and item_type = %s'
            cursor.execute(sql, (sheet_id, type_id))
            sql = 'delete from vsongsheet where sheet_id = %s'
            cursor.execute(sql, sheet_id)
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '删除歌单成功'
            })
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data['msg'] = e.args
            return jsonify(json_data)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def sheet_add_song(sheet_id, song_id, user_id):
        json_data = dict()
        conn = get_conn()
        cursor = conn.cursor()
        try:
            sql = 'select owner from vsongsheet where sheet_id = %s'
            cursor.execute(sql, sheet_id)
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '歌单不存在'
                })
            if str(rows[0][0]) != user_id:
                return jsonify({
                    'code': -1,
                    'msg': '歌单属于userid: ' + str(rows[0][0])
                })
            sql = 'insert into song_songsheet(sheet_id, song_id) values(%s,%s)'
            cursor.execute(sql, (sheet_id, song_id))
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '歌单添加歌曲成功'
            })
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data['msg'] = e.args
            return jsonify(json_data)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def sheet_delete_song(sheet_id, song_id, user_id):
        json_data = dict()
        conn = get_conn()
        cursor = conn.cursor()
        try:
            sql = 'select owner from vsongsheet where sheet_id = %s'
            cursor.execute(sql, sheet_id)
            rows = cursor.fetchall()
            if len(rows) == 0:
                return jsonify({
                    'code': -1,
                    'msg': '歌单不存在'
                })
            if str(rows[0][0]) != user_id:
                return jsonify({
                    'code': -1,
                    'msg': '歌单属于userid: ' + str(rows[0][0])
                })
            sql = 'delete from song_songsheet where sheet_id = %s and song_id = %s'
            cursor.execute(sql, (sheet_id, song_id))
            conn.commit()
            return jsonify({
                'code': 0,
                'msg': '歌单删除歌曲成功'
            })
        except Exception as e:
            conn.rollback()
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data['msg'] = e.args
            return jsonify(json_data)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def sheets_to_jsonify(uid, sheets):
        json_data = dict()
        try:
            json_data['code'] = 0
            json_data['data'] = []
            for sheet in sheets:
                json_data['data'].append(sheet.to_data(uid))
            return jsonify(json_data)
        except Exception as e:
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data.pop('data')
            json_data['msg'] = e.args
            return jsonify(json_data)

    def __str__(self):
        return "sheet_id:{} owner:{} sheet_name:{}".format(self.sheet_id, self.owner, self.sheet_name)


class Song(object):
    def __init__(self, song_id, song_name, song_img, play_times, thumbs_up_num, song_album, music163_id, song_dt):
        self.song_id = song_id
        self.song_name = song_name
        self.song_img = song_img
        self.play_times = play_times
        self.thumbs_up_num = thumbs_up_num
        self.song_album = song_album
        self.music163_id = music163_id
        self.song_dt = song_dt

    def to_data(self, user_id):
        res = {'song_id': self.song_id, 'song_name': self.song_name, 'song_album': self.song_album,
               'song_img': self.song_img, 'play_times': self.play_times, 'thumbs_up_num': self.thumbs_up_num,
               'song_dt': self.song_dt, 'music163_id': self.music163_id}
        conn = get_conn()
        cursor = conn.cursor()
        if res['song_album'] is not None:
            album_id = int(res['song_album'])
            sql = 'select sheet_name from vsongsheet where sheet_id = %s'
            cursor.execute(sql, album_id)
            res['song_album'] = cursor.fetchall()[0][0]
        singers = []
        singer_ids = []
        sql = 'select singer_id from song_singer where song_id = %s'
        cursor.execute(sql, res['song_id'])
        rows = cursor.fetchall()
        for row in rows:
            singer_ids.append(row[0])
        for singer_id in singer_ids:
            sql = 'select singer_name from vsinger where singer_id = %s'
            cursor.execute(sql, singer_id)
            singers.append(cursor.fetchall()[0][0])
        res['singers'] = singers
        sql = "select * from vthumbsup where user_id = %s and item_id = %s and item_type = 1"
        cursor.execute(sql, (user_id, self.song_id))
        if len(cursor.fetchall()) == 0:
            res['is_thumbs_up'] = False
        else:
            res['is_thumbs_up'] = True
        cursor.close()
        conn.close()
        return res

    @staticmethod
    def query_all():
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select song_id, song_name, song_img, play_times, thumbs_up_num, song_album, music163_id, song_dt from vsong'
        cursor.execute(sql)
        rows = cursor.fetchall()
        songs = []
        for row in rows:
            songs.append(Song(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('Song.query_all() success')
        return songs

    @staticmethod
    def query_by_name(name):
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select song_id, song_name, song_img, play_times, thumbs_up_num, song_album, music163_id, song_dt from vsong where song_name like %s'
        cursor.execute(sql, '%' + name + '%')
        rows = cursor.fetchall()
        songs = []
        for row in rows:
            songs.append(Song(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('Song.query_by_name() success')
        return songs

    @staticmethod
    def query_by_singer(singer_id):
        conn = get_conn()
        cursor = conn.cursor()
        song_ids = []
        sql = 'select song_id from song_singer where singer_id = %s'
        cursor.execute(sql, singer_id)
        rows = cursor.fetchall()
        for row in rows:
            song_ids.append(row[0])
        songs = []
        for song_id in song_ids:
            sql = 'select song_id, song_name, song_img, play_times, thumbs_up_num, song_album, music163_id, song_dt from vsong where song_id = %s'
            cursor.execute(sql, song_id)
            row = cursor.fetchall()[0]
            songs.append(Song(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('Song.query_by_singer() success')
        return songs

    @staticmethod
    def query_by_sheet(sheet_id):
        conn = get_conn()
        cursor = conn.cursor()
        song_ids = []
        sql = 'select song_id from song_songsheet where sheet_id = %s'
        cursor.execute(sql, sheet_id)
        rows = cursor.fetchall()
        for row in rows:
            song_ids.append(row[0])
        songs = []
        for song_id in song_ids:
            sql = 'select song_id, song_name, song_img, play_times, thumbs_up_num, song_album, music163_id, song_dt from vsong where song_id = %s'
            cursor.execute(sql, song_id)
            row = cursor.fetchall()[0]
            songs.append(Song(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cursor.close()
        conn.close()
        print('Song.query_by_sheet() success')
        return songs

    @staticmethod
    def songs_to_jsonify(user_id, songs):
        json_data = dict()
        try:
            json_data['code'] = 0
            json_data['data'] = []
            for song in songs:
                json_data['data'].append(song.to_data(user_id))
            return jsonify(json_data)
        except Exception as e:
            print(e.args)
            print(traceback.format_exc())
            json_data['code'] = -1
            json_data.pop('data')
            json_data['msg'] = e.args
            return jsonify(json_data)

    def __str__(self):
        return "song_id:{} song_name:{}".format(self.song_id, self.song_name)

    @staticmethod
    def add_from_music163(indict):
        music163_id = indict['id']
        conn = get_conn()
        cursor = conn.cursor()
        sql = 'select * from vsong where music163_id = %s'
        cursor.execute(sql, music163_id)
        if len(cursor.fetchall()) == 1:
            return
        singer_ids = []
        for i in indict['ar']:
            singer163_id = i['id']
            sql = 'select singer_id from vsinger where singer163_id = %s'
            cursor.execute(sql, singer163_id)
            rows = cursor.fetchall()
            if len(rows) == 1:
                singer_ids.append(rows[0][0])
                continue
            else:
                sql = 'insert into vsinger(singer_name, play_times, thumbs_up_num, singer163_id) values(%s,0,0,%s)'
                cursor.execute(sql, (i['name'], singer163_id))
                singer_ids.append(cursor.lastrowid)
        sheet163_id = indict['al']['id']
        sql = 'select sheet_id from vsongsheet where sheet163_id = %s'
        cursor.execute(sql, sheet163_id)
        rows = cursor.fetchall()
        sheet_id = 0
        if len(rows) == 1:
            sheet_id = rows[0][0]
        else:
            sql = 'insert into vsongsheet(sheet_name, owner, sheet_img, play_times, thumbs_up_num, follow_num, sheet163_id) values(%s,0,%s,0,0,0,%s)'
            cursor.execute(sql, (indict['al']['name'], indict['al']['picUrl'], singer163_id))
            sheet_id = cursor.lastrowid
        sql = 'insert into vsong(song_name, song_album, song_img, play_times, thumbs_up_num, music163_id, song_dt) values(%s,%s,%s,0,0,%s,%s)'
        cursor.execute(sql, (indict['name'], sheet_id, indict['al']['picUrl'], music163_id, indict['dt']))
        song_id = cursor.lastrowid
        for i in singer_ids:
            sql = 'insert into song_singer(singer_id, song_id) values(%s,%s)'
            cursor.execute(sql, (i, song_id))
        sql = 'insert into song_songsheet(sheet_id, song_id) values(%s,%s)'
        cursor.execute(sql, (sheet_id, song_id))
        conn.commit()
        cursor.close()
        conn.close()
