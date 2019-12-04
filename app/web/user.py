import json
import multidict
import pymysql
import datetime
from flask import current_app, request, jsonify, session
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.forms.auth import ResetPasswordForm
from app.forms.user import genderForm, birthdayForm
from app.model.user import User, get_user
from app.web import web


# 查找用户
@web.route('/v1/user/search', methods=['POST'])
# @login_required
def searchUser():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()
    sql = ""
    if request.form.get('uid') is None:
        sql = "SELECT * FROM vuser WHERE user_id = %s" % (session.get('user_id'))
    else:
        sql = "SELECT * FROM vuser WHERE user_id = %s" % (request.form['uid'])
    try:
        cursor.execute(sql)
        user = cursor.fetchone()
        userObject = User()
        userObject.set_attr(user, session.get('user_id'))
        res = userObject.__dict__
        res.pop('password')

        # u = userObject.__dict__
        return jsonify({
            "code": 200,
            "user": res
        })
    except:
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()


# 查找自己关注的用户
@web.route('/v1/user/searchfollow', methods=['POST'])
# @login_required
def searchfollow():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()
    uid = session.get("user_id")
    sql = "SELECT to_user_id FROM vfollow WHERE user_id = %s" % (uid)
    try:
        cursor.execute(sql)
        userIdArray = cursor.fetchall()
        userArray = []
        for row in userIdArray:
            id = row[0]
            sql = "SELECT * FROM vuser WHERE user_id = %s" % (id)
            cursor.execute(sql)
            user = cursor.fetchone()
            userObject = User()
            userObject.set_attr(user, session.get('user_id'))
            userArray.append(userObject)
        return jsonify({
            "code": 200,
            "userArray": json.loads(json.dumps(userArray, default=lambda o: o.__dict__))
        })
    except:
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()


# 关注
@web.route('/v1/user/follow', methods=['POST'])
# @login_required
def follow():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()

    try:
        user = get_user(request.form['toUserid'])
        if user is None:
            return jsonify({
                "code": -1,
                "errMsg": "关注用户不存在"
            })
        uid = session.get("user_id")
        sql = "INSERT INTO vfollow(user_id,to_user_id) VALUES (%s,%s)" % (uid, request.form['toUserid'])
        cursor.execute(sql)
        db.commit()
        return jsonify({
            "code": 200
        })
    except:
        db.rollback()
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()


# 是否关注
@web.route('/v1/user/is_followed', methods=['POST'])
# @login_required
def is_followed():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()

    try:
        user = get_user(request.form['toUserid'])
        if user is None:
            return jsonify({
                "code": -1,
                "errMsg": "关注用户不存在"
            })
        uid = session.get("user_id")
        sql = "select * from violet.vfollow where user_id = %s and to_user_id = %s" % (uid, request.form['toUserid'])
        cursor.execute(sql)
        return jsonify({
            "code": 0,
            "is_followed": len(cursor.fetchall()) == 1
        })
    except:
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        cursor.close()
        db.close()


# 取消关注
@web.route("/v1/user/unfollow", methods=['POST'])
# @login_required
def unfollow():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()

    try:
        user = get_user(request.form['toUserid'])
        if user is None:
            return jsonify({
                "code": -1,
                "errMsg": "关注用户不存在"
            })
        # uid = session.get("user_id")
        uid = session.get("user_id")
        sql = "DELETE FROM vfollow WHERE user_id=%s and to_user_id = %s" % (uid, request.form['toUserid'])
        cursor.execute(sql)
        db.commit()
        return jsonify({
            "code": 200
        })
    except:
        db.rollback()
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()


# 修改用户个人信息
@web.route("/v1/user/modify", methods=['POST'])
# @login_required
def modifyUser():
    uid = session.get("user_id")
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()
    try:
        user = get_user(uid)
        gender = request.form.get("gender", default=None)
        nickname = request.form.get("nickname", default=None)
        motto = request.form.get('motto', default=None)
        info = request.form.get('info', default=None)
        birthday = request.form.get('birthday', default=None)
        if gender is not None:
            form = multidict.MultiDict([('gender', gender)])
            GForm = genderForm(form)
            if GForm.validate() is not True:
                return jsonify({
                    "code": -1,
                    "errMsg": "请选择正确的用户性别"
                })
            else:
                user.gender = gender
        if birthday is not None:
            form = multidict.MultiDict([('birthday', birthday)])
            birthForm = birthdayForm(form)
            if birthForm.validate() is not True:
                return jsonify({
                    "code": -1,
                    "errMsg": "请选择正确的用户生日"
                })
            else:
                user.birthday = birthday
        if nickname is not None:
            user.userNickName = nickname
        if motto is not None:
            user.motto = motto
        if info is not None:
            user.info = info
        sql = "UPDATE vuser SET user_nickname = '%s' ,gender = %s, birthday = '%s', motto = '%s', info = '%s' WHERE user_id = %s" % (
            user.userNickName, user.gender, user.birthday, user.motto, user.info, uid)
        cursor.execute(sql)
        db.commit()
        return jsonify({
            "code": 200
        })
    except:
        db.rollback()
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()


# 用户生日提醒/除了用户自己，还返回了关注该用户的用户数组，和该用户的生日
# 这里的估计还有多少天到用户生日是粗略的，不顾问题不大
@web.route("/v1/user/reminder/birth", methods=['POST'])
# @login_required
def birthReminder():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()

    try:
        uid = session.get("user_id")
        sql = "SELECT birthday FROM vuser WHERE  user_id = %s" % (uid)
        cursor.execute(sql)
        birthday = cursor.fetchone()
        if birthday[0] is None:
            return jsonify({
                "code": -1
            })
        month = birthday[0].month
        day = birthday[0].day
        currentMonth = datetime.datetime.now().month
        currentDay = datetime.datetime.now().day
        diff = (month - currentMonth) * 30 + day - currentDay
        if 0 <= diff <= 3:
            sql = "SELECT user_id FROM vfollow WHERE to_user_id = %s" % (uid)
            cursor.execute(sql)
            userIdArray = cursor.fetchall()
            userArray = []
            for row in userIdArray:
                id = row[0]
                sql = "SELECT * FROM vuser WHERE user_id = %s" % (id)
                cursor.execute(sql)
                user = cursor.fetchone()
                userObject = User()
                userObject.set_attr(user, session.get('user_id'))
                userArray.append(userObject)
            return jsonify({
                "code": 200,
                "userArray": json.loads(json.dumps(userArray, default=lambda o: o.__dict__)),
                "birthday": birthday[0].strftime("%Y-%m-%d")
            })
        else:
            return jsonify({
                "code": -1
            })
    except:
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()


# 修改用户密码
@web.route("/v1/user/changepwd", methods=['POST'])
# @login_required
def changePassword():
    uid = session.get("user_id")
    passwordFrom = ResetPasswordForm(request.form)
    if passwordFrom.validate():
        form = ResetPasswordForm(request.form)
        if form.validate():
            new_password = form.data['password1']
            db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                                 password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                                 database=current_app.config['DATABASE'],
                                 charset=current_app.config['CHARSET'])
            cursor = db.cursor()
            password = generate_password_hash(new_password)
            sql = "UPDATE vuser SET password = '%s' WHERE user_id = %s" % (password, uid)
            try:
                cursor.execute(sql)
                db.commit()
                return jsonify({
                    "code": 200
                })
            except:
                db.rollback()
                return jsonify({
                    "code": -1,
                    "errMsg": "密码修改失败"
                })
            finally:
                db.close()


@web.route("/v1/user/searchByName", methods=['post'])
def searchByName():
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'], charset=current_app.config['CHARSET'])
    cursor = db.cursor()

    try:
        nickname = request.args['nickname'].strip()
        sql = "SELECT user_id FROM vuser WHERE  user_nickname LIKE  '%%%s%%'" % (nickname)
        cursor.execute(sql)
        userIdArray = cursor.fetchall()
        userArray = []
        for row in userIdArray:
            id = row[0]
            sql = "SELECT * FROM vuser WHERE user_id = %s" % (id)
            cursor.execute(sql)
            user = cursor.fetchone()
            userObject = User()
            userObject.set_attr(user, session.get('user_id'))
            userArray.append(userObject)

        return jsonify({
            "code": 200,
            "userArray": json.loads(json.dumps(userArray, default=lambda o: o.__dict__)),
        })

    except:
        return jsonify({
            "code": -1,
            "errMsg": "数据库操作失败"
        })
    finally:
        db.close()
