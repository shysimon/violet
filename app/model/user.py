import pymysql
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash

from app import login_manager


class User(UserMixin):
    userId = None
    userNickName = None
    password = None
    gender = None
    birthday = None
    motto = None
    thumbsUpNum = None
    userType = None
    info = None  # 简介
    email = None
    zoneCount = None
    fansCount = None
    followCount = None
    isFollowed = None

    # 从数据库中取出的信息赋值给user对象，因为数据库取出的信息是元组，所以这里好像不能通过字段名获得相应值，只能通过下标
    def set_attr(self, user, nowid):
        self.userId = user[0]
        self.userNickName = user[1]
        self.password = user[2]
        self.gender = user[3]
        self.birthday = str(user[4])
        self.motto = user[5]
        self.thumbsUpNum = user[6]
        self.userType = user[7]
        self.info = user[8]  # 简介
        self.email = user[9]
        db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                             password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                             database=current_app.config['DATABASE'],
                             charset=current_app.config['CHARSET'])
        cursor = db.cursor()
        sql = 'select count(*) from violet.vzone where user_id = %s'
        cursor.execute(sql, self.userId)
        self.zoneCount = cursor.fetchall()[0][0]
        sql = 'select count(*) from violet.vfollow where user_id = %s'
        cursor.execute(sql, self.userId)
        self.followCount = cursor.fetchall()[0][0] - 1
        sql = 'select count(*) from violet.vfollow where to_user_id = %s'
        cursor.execute(sql, self.userId)
        self.fansCount = cursor.fetchall()[0][0] - 1
        sql = "select * from violet.vfollow where user_id = %s and to_user_id = %s" % (nowid, self.userId)
        cursor.execute(sql)
        self.isFollowed = len(cursor.fetchall()) == 1
        cursor.close()
        db.cursor()

    def get_id(self):
        return self.userId

    @staticmethod
    def getUserByEmail(email):
        db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                             password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                             database=current_app.config['DATABASE'],
                             charset=current_app.config['CHARSET'])
        cursor = db.cursor()
        sql = "SELECT * FROM vuser WHERE email = '%s'" % (email)

        try:
            cursor.execute(sql)
            user = cursor.fetchone()
            userObject = User()
            userObject.set_attr(user)
            return userObject
        except:
            print("Error: unable to fetch data")
        finally:
            db.close()

    def generate_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({"id": self.userId}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        uid = data.get("id")
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
        except:
            print("更新失败")
        finally:
            db.close()
        return True


@login_manager.user_loader
def get_user(userid):
    db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                         password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                         database=current_app.config['DATABASE'],
                         charset=current_app.config['CHARSET'])
    cursor = db.cursor()
    sql = "SELECT * FROM vuser WHERE user_id = %s" % (int(userid))

    try:
        cursor.execute(sql)
        user = cursor.fetchone()
        userObject = User()
        userObject.set_attr(user)
        return userObject
    except:
        print("Error: unable to fetch data")
    finally:
        db.close()
