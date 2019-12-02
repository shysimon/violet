import pymysql
from flask import request, current_app, jsonify, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.forms.auth import RegisterForm, LoginForm, EmailForm, ResetPasswordForm
from app.lib.email import send_mail
from app.model.user import User
from . import web


@web.route('/v1/auth/register', methods=['POST'])
def register():
    form = RegisterForm(request.args)
    if form.validate():
        db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                             password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                             database=current_app.config['DATABASE'],
                             charset=current_app.config['CHARSET'])
        cursor = db.cursor()

        # SQL 插入语句
        sql = "INSERT INTO vuser(user_nickname,password, email) VALUES ('%s', '%s', '%s' )" % \
              (form.data['nickname'], generate_password_hash(form.data['password']), form.data['email'])
        try:
            cursor.execute(sql)
            last_id = cursor.lastrowid
            sql = "INSERT INTO vfollow(user_id,to_user_id) VALUES (%s,%s)" % (last_id, last_id)
            cursor.execute(sql)
            # 执行sql语句
            db.commit()
        except Exception as e:
            # 发生错误时回滚
            db.rollback()
            return jsonify({
                "code": "-1",
                "errMsg": "数据库操作失败"
            })
        finally:
            # 关闭数据库连接
            db.close()
        return jsonify({
            "code": "200"
        })
    else:
        return jsonify({
            "code": "-1",
            "errMsg": form.errors
        })


@web.route('/v1/auth/login', methods=['POST'])
def login():
    form = LoginForm(request.args)
    if form.validate():
        db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                             password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                             database=current_app.config['DATABASE'],
                             charset=current_app.config['CHARSET'])
        cursor = db.cursor()

        # SQL 插入语句
        sql = "SELECT * FROM vuser WHERE email = '%s'" % (form.data['email'])
        try:
            cursor.execute(sql)
            user = cursor.fetchone()
            userObject = User()
            userObject.set_attr(user)
            if user and check_password_hash(userObject.password, form.data['password']):
                login_user(userObject)
                return jsonify({
                    "code": 200,
                    "Msg": "登录成功"
                })
            else:
                return jsonify({
                    "code": "-1",
                    "errMsg": "账号或密码输入错误"
                })
        except Exception as e:
            return jsonify({
                "code": "-1",
                "errMsg": "数据库操作错误"
            })
        finally:
            # 关闭数据库连接
            db.close()
    else:
        return jsonify({
            "code": "-1",
            "errMsg": form.errors
        })


@web.route('/v1/auth/reset/password', methods=['POST'])
def forget_password_request():
    form = EmailForm(request.args)
    if form.validate():
        account_email = form.email.data
        user = User.getUserByEmail(account_email)
        if user is not None:
            send_mail(account_email, "重置你的密码", 'email/reset_password.html', user=user, token=user.generate_token())
            return jsonify({
                "code": "200"
            })
        else:
            return jsonify({
                "code": "-1",
                "errMsg": "邮箱不存在"
            })
    else:
        return jsonify({
            "code": "-1",
            "errMsg": form.errors
        })


@web.route('/v1/auth/reset/password/<token>', methods=['POST'])
def forget_password(token):
    form = ResetPasswordForm(request.args)
    if form.validate():
        success = User.reset_password(token, form.password1.data)
        if success:
            return jsonify({
                "code": "200"
            })
        else:
            return jsonify({
                "code": "-1",
                "errMsg": "密码修改失败"
            })


@web.route('/v1/auth/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return jsonify({
        "code": "200"
    })
