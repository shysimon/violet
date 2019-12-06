from flask import Flask, jsonify, request, session
from app.web.violet_group_function import Group
from app.web.violet_post_function import Post
from . import web


# app = Flask(__name__)


# @web.route('/')
# def hello_world():
#     return 'Hello World!'


@web.route('/v1/group/load_group', methods=['POST', 'GET'])
def load_group():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    return Group.load_group(user_id)


@web.route('/v1/group/index_groups', methods=['POST', 'GET'])
def index_groups():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    return Group.load_group_top5(user_id)


@web.route('/v1/group/load_group_by_id', methods=['POST', 'GET'])
def load_group_by_id():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    group_id = request.form.get('group_id')
    if group_id is None:
        return jsonify({
            'code': '-1',
            'errMsg': '缺少参数group_id'
        })
    return Group.load_group_by_id(group_id, user_id)


@web.route('/v1/group/search_group', methods=['POST', 'GET'])
def search_group():
    keyword = None
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    if request.method == 'POST':
        # user_id = 1
        keyword = request.form.get('keyword')
    if request.method == 'GET':
        # user_id = 1
        keyword = request.args.get('keyword')
    if keyword is None:
        return jsonify({
            'code': '-1',
            'errMsg': '缺少参数keyword'
        })
    return Group.search_group(keyword, user_id)


@web.route('/v1/group/add_group', methods=['POST', 'GET'])
def add_group():
    user_id = None
    group_name = None
    info = None
    thumbs_up_num = None
    follow_num = None

    if request.method == 'POST':
        user_id = session.get('user_id')
        # user_id = 1
        group_name = request.form.get('group_name')
        info = request.form.get('info')
        thumbs_up_num = request.form.get('thumbs_up_num')
        follow_num = request.form.get('follow_num')
    if request.method == 'GET':
        user_id = session.get('user_id')
        # user_id = 1
        group_name = request.args.get('group_name')
        info = request.args.get('info')
        thumbs_up_num = request.args.get('thumbs_up_num')
        follow_num = request.args.get('follow_num')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数owner'
        })
    if group_name is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_name'
        })
    if info is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数info'
        })
    if thumbs_up_num is None:
        thumbs_up_num = 0
    if follow_num is None:
        follow_num = 1
    return Group.add_group(user_id, group_name, info, thumbs_up_num=thumbs_up_num, follow_num=follow_num)


@web.route('/v1/group/delete_group', methods=['POST', 'GET'])
def delete_group():
    user_id = None
    group_id = None

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        # user_id = 1
        group_id = request.form.get('group_id')
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        # user_id = 1
        group_id = request.args.get('group_id')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if group_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_id'
        })
    return Group.delete_group(group_id, user_id)


@web.route('/v1/group/invite_friend', methods=['POST', 'GET'])
def invite_friend():
    user_id = None
    friend_id = None
    group_id = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        # user_id = 1
        friend_id = request.form.get('friend_id')
        group_id = request.form.get('group_id')
    if request.method == 'GET':
        user_id = session.get('user_id')
        # user_id = 1
        friend_id = request.args.get('friend_id')
        group_id = request.args.get('group_id')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if friend_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数friend_id'
        })
    if group_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_id'
        })
    return Group.invite_user(friend_id, group_id)


@web.route('/v1/post/load_post', methods=['POST', 'GET'])
def load_post():
    user_id = None
    group_id = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        group_id = request.form.get('group_id')
    if request.method == 'GET':
        user_id = session.get('user_id')
        group_id = request.args.get('group_id')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if group_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_id'
        })
    return Post.load_post(group_id, user_id)

@web.route('/v1/post/load_post_by_id', methods=['POST', 'GET'])
def load_post_by_id():
    user_id = None
    post_id = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        post_id = request.form.get('post_id')
    if request.method == 'GET':
        user_id = session.get('user_id')
        post_id = request.args.get('post_id')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if post_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_id'
        })
    return Post.load_post_by_id(post_id, user_id)

@web.route('/v1/post/index_posts', methods=['POST', 'GET'])
def index_posts():
    user_id = session.get('user_id')
    if user_id is None:
        user_id = 0
    return Post.load_post_top5(user_id)


@web.route('/v1/post/add_post', methods=['POST', 'GET'])
def add_post():
    user_id = None
    group_id = None
    post_title = None
    content = None
    thumbs_up_num = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        # user_id = 1
        group_id = request.form.get('group_id')
        post_title = request.form.get('post_title')
        content = request.form.get('content')
        thumbs_up_num = request.form.get('thumbs_up_num')
    if request.method == 'GET':
        user_id = session.get('user_id')
        # user_id = 1
        group_id = request.args.get('group_id')
        post_title = request.args.get('post_title')
        content = request.args.get('content')
        thumbs_up_num = request.args.get('thumbs_up_num')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if group_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_id'
        })
    if post_title is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数post_title'
        })
    if thumbs_up_num is None:
        thumbs_up_num = 0
    if content is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数content'
        })
    return Post.add_post(group_id, user_id, post_title, content, thumbs_up_num)


@web.route('/v1/post/delete_post', methods=['POST', 'GET'])
def delete_post():
    user_id = None
    post_id = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        # user_id = 1
        post_id = request.form.get('post_id')
    if request.method == 'GET':
        user_id = session.get('user_id')
        # user_id = 1
        post_id = request.args.get('post_id')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if post_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数post_id'
        })
    return Post.delete_post(post_id)


@web.route('/v1/post/modify_post', methods=['POST', 'GET'])
def modify_post():
    user_id = None
    post_id = None
    new_content = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        # user_id = 1
        post_id = request.form.get('post_id')
        new_content = request.form.get('new_content')
    if request.method == 'GET':
        user_id = session.get('user_id')
        # user_id = 1
        post_id = request.args.get('post_id')
        new_content = request.args.get('new_content')
    if user_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数user_id'
        })
    if post_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数post_id'
        })
    if new_content is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数new_content'
        })
    return Post.modify_post(post_id, new_content)


@web.route('/v1/post/search_post', methods=['POST', 'GET'])
def search_post():
    user_id = None
    keyword = None
    group_id = None
    if request.method == 'POST':
        user_id = session.get('user_id')
        # user_id = 1
        keyword = request.form.get('keyword')
        group_id = request.form.get('group_id')
    if request.method == 'GET':
        user_id = session.get('user_id')
        # user_id = 1
        keyword = request.args.get('keyword')
        group_id = request.args.get('group_id')
    if user_id is None:
        user_id = 0
        # return jsonify({
        #     'code': -1,
        #     'errMsg': '缺少参数user_id'
        # })
    if keyword is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数keyword'
        })
    if group_id is None:
        return jsonify({
            'code': -1,
            'errMsg': '缺少参数group_id'
        })

    return Post.search_post(keyword, group_id, user_id)

# if __name__ == '__main__':
#     app.run()
#
