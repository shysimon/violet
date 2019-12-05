from flask import Flask, request, jsonify, session
from flask_login import login_required
from . import web
import requests

from app.web.violet_songsheet_functions import SongSheet, Song

# app = Flask(__name__)

# @web.route('/')
# def hello_world():
#     return 'Hello World!'


'''
查询歌单返回
{
    "code":0,
    "data":[
        {
            "follow_num":       关注数量,
            "info":             歌单介绍信息,
            "owner":            所有者的名字，若是专辑，则为 专辑 两字"\u4e13\u8f91",
            "play_times":       播放量,
            "sheet_id":         专辑主键,
            "sheet_img":        专辑图片,
            "sheet_name":       专辑名字"\u4e13\u8f911",
            "thumbs_up_num":    点赞数
            "is_followed":      是否被关注 true/false
            "is_thumbs_up":     是否被点赞 true/false
        }
    ]
}
查询歌曲返回
{
    "code":0,
    "data":[
        {
            "play_times":       播放量,
            "singers":          歌手（是一个list可能有多个歌手）["\u8521\u5f90\u5764","\u7bee\u7403"],
            "song_album":       专辑名称，若不存在专辑则返回null"\u4e13\u8f911",
            "song_id":          歌曲主键,
            "song_img":         歌曲图片,
            "song_name":        歌曲名"wait wait wait",
            "thumbs_up_num":    点赞数
            "is_thumbs_up":     是否被点赞 true/false
        }
    ]
}

'''


# 读取所有歌单信息
# 无参数
@web.route('/v1/sheet/all_sheets', methods=['GET', 'POST'])
def all_sheets():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    limit = request.form.get('limit')
    if limit is None:
        limit = 50
    return SongSheet.sheets_to_jsonify(user_id, SongSheet.query_all(limit))


# 读取主页排前十歌单信息
# 无参数
@web.route('/v1/sheet/index_sheets', methods=['GET', 'POST'])
def index_sheets():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    return SongSheet.sheets_to_jsonify(user_id, SongSheet.query_top10())


# 搜索属于某user的歌单信息
@web.route('/v1/sheet/sheets_by_id', methods=['GET', 'POST'])
def sheets_by_id():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    sheet_id = None
    if request.method == 'POST':
        sheet_id = request.form.get('sheet_id')
    if request.method == 'GET':
        sheet_id = request.args.get('sheet_id')
    if sheet_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数sheet_id'
        })
    return SongSheet.sheets_details_to_jsonify(user_id, SongSheet.query_by_id(sheet_id),
                                               Song.query_by_sheet(sheet_id))


# 搜索属于某user的歌单信息
# 需要登录
@web.route('/v1/sheet/sheets_by_owner', methods=['GET', 'POST'])
# @login_required
def sheets_by_owner():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    owner = request.form.get('user_id')
    if owner is None:
        owner = 0
    return SongSheet.sheets_to_jsonify(user_id, SongSheet.query_by_owner(owner))


# 通过歌单名词模糊搜索歌单
# 参数'name':歌单模糊查询词，不需要%通配符
@web.route('/v1/sheet/sheets_by_name', methods=['GET', 'POST'])
def sheets_by_name():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    name = None
    if request.method == 'POST':
        name = request.form.get('name')
    if request.method == 'GET':
        name = request.args.get('name')
    if name is None:
        return all_sheets()
    return SongSheet.sheets_to_jsonify(user_id, SongSheet.query_by_name(name))


# 搜索某user关注的所有歌单（非所有者）
# 需要登录
@web.route('/v1/sheet/sheets_by_user', methods=['GET', 'POST'])
# @login_required
def sheets_by_user():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    q_user_id = request.form.get('user_id')
    if q_user_id is None:
        q_user_id = 0
    return SongSheet.sheets_to_jsonify(user_id, SongSheet.query_by_user(q_user_id))


# 创建歌单
# 参数'sheet_name':歌单名称
# 需要登录
# 'file':专辑图片，（可选项）
@web.route('/v1/sheet/create_sheet', methods=['GET', 'POST'])
# @login_required
def create_sheet():
    sheet_name = None
    user_id = session.get("user_id")
    sheet_img = None
    if request.method == 'POST':
        sheet_name = request.form.get('sheet_name')
        sheet_img = request.files.get('file')
    if request.method == 'GET':
        sheet_name = request.args.get('sheet_name')
        sheet_img = request.files.get('file')
    if sheet_name is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数sheet_name'
        })
    return SongSheet.create_sheet(sheet_name, user_id, sheet_img)


# 删除歌单
# 参数'sheet_id':歌单id
# 需要登录
# 注意会删除 歌曲-歌单 表中信息，会删除对应点赞、评论信息，会删除 用户-歌单 表中信息
# 若owner不符合，不会删除
@web.route('/v1/sheet/delete_sheet', methods=['GET', 'POST'])
# @login_required
def delete_sheet():
    sheet_id = None
    user_id = session.get("user_id")
    if request.method == 'POST':
        sheet_id = request.form.get('sheet_id')
    if request.method == 'GET':
        sheet_id = request.args.get('sheet_id')
    if sheet_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数sheet_id'
        })
    return SongSheet.delete_sheet(sheet_id, user_id)


# 歌单添加歌曲
# 参数'sheet_id':歌单id
# 'song_id':歌曲id
# 需要登录
@web.route('/v1/sheet/sheet_add_song', methods=['GET', 'POST'])
# @login_required
def sheet_add_song():
    user_id = session.get("user_id")
    sheet_id = None
    song_id = None
    if request.method == 'POST':
        sheet_id = request.form.get('sheet_id')
        song_id = request.form.get('song_id')
    if request.method == 'GET':
        sheet_id = request.args.get('sheet_id')
        song_id = request.args.get('song_id')
    if sheet_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数sheet_name'
        })
    if song_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数song_id'
        })
    return SongSheet.sheet_add_song(sheet_id, song_id, user_id)


# 歌单删除歌曲
# 参数'sheet_id':歌单id
# 'song_id':歌曲id
# 若个单中没有该歌曲，也不会报错
# 需要登录
@web.route('/v1/sheet/sheet_delete_song', methods=['GET', 'POST'])
# @login_required
def sheet_delete_song():
    user_id = session.get("user_id")
    sheet_id = None
    song_id = None
    if request.method == 'POST':
        sheet_id = request.form.get('sheet_id')
        song_id = request.form.get('song_id')
    if request.method == 'GET':
        sheet_id = request.args.get('sheet_id')
        song_id = request.args.get('song_id')
    if sheet_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数sheet_name'
        })
    if song_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数song_id'
        })
    return SongSheet.sheet_delete_song(sheet_id, song_id, user_id)


# 读取所有歌曲信息
# 无参数
@web.route('/v1/song/all_songs', methods=['GET', 'POST'])
def all_songs():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    return Song.songs_to_jsonify(user_id, Song.query_all())


# 通过歌曲名查询歌曲
# 参数'name':歌曲名称
@web.route('/v1/song/songs_by_name', methods=['GET', 'POST'])
def songs_by_name():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    name = None
    if request.method == 'POST':
        name = request.form.get('name')
    if request.method == 'GET':
        name = request.args.get('name')
    if name is None:
        return all_songs()
    else:
        url = "http://shysimon.cn:3000/v1/search"
        params = {"keywords": name}
        res = requests.get(url, params)
        for i in res.json()['result']['songs']:
            Song.add_from_music163(i)
    return Song.songs_to_jsonify(user_id, Song.query_by_name(name))


# 通过歌手查询歌曲
# 参数'singer_id':歌手主键
@web.route('/v1/song/songs_by_singer', methods=['GET', 'POST'])
def songs_by_singer():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    singer_id = None
    if request.method == 'POST':
        singer_id = request.form.get('singer_id')
    if request.method == 'GET':
        singer_id = request.args.get('singer_id')
    if singer_id is None:
        return all_songs()
    return Song.songs_to_jsonify(user_id, Song.query_by_singer(singer_id))


# 通过歌单查询歌曲
# 参数'sheet_id':歌单主键
@web.route('/v1/song/songs_by_sheet', methods=['GET', 'POST'])
def songs_by_sheet():
    user_id = session.get("user_id")
    if user_id is None:
        user_id = 0
    sheet_id = None
    if request.method == 'POST':
        sheet_id = request.form.get('sheet_id')
    if request.method == 'GET':
        sheet_id = request.args.get('sheet_id')
    if sheet_id is None:
        return all_songs()
    return Song.songs_to_jsonify(user_id, Song.query_by_sheet(sheet_id))


@web.route('/v1/song/geturl', methods=['GET', 'POST'])
def get_music163_url():
    music163_id = None
    if request.method == 'POST':
        music163_id = request.form.get('music163_id')
    if request.method == 'GET':
        music163_id = request.args.get('music163_id')
    if music163_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数music163_id'
        })
    song_id = request.form.get('song_id')
    if song_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数song_id'
        })
    Song.play(song_id)
    return jsonify({
        'code': 0,
        'url': get_url_from_music163(music163_id),
        'lrc': get_lyric_from_music163(music163_id)
    })


def get_url_from_music163(music163_id):
    url = "http://shysimon.cn:3000/v1/music/url"
    params = {"id": music163_id, "br": 320000}
    r = requests.get(url, params)
    return r.json()['data'][0]['url']


def get_lyric_from_music163(music163_id):
    url = "http://shysimon.cn:3000/v1/lyric"
    params = {"id": music163_id}
    r = requests.get(url, params)
    return r.json()['lrc']['lyric']

# if __name__ == '__main__':
#     app.run()
