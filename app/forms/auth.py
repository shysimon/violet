import pymysql
from flask import current_app
from wtforms import Form, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo


class RegisterForm(Form):
    email = StringField(validators=[DataRequired(message="邮箱不能为空"), Length(8, 64, message="邮箱长度过短"), Email(message="电子邮箱不符合规范")])

    password = PasswordField(validators=[DataRequired(message="密码不可以为空，请输入你的密码")])

    nickname = StringField(validators=[DataRequired(message="昵称不能为空"), Length(2, 10, message='昵称至少需要两个字符，最多10个字符')])

    def validate_email(self, field):
        db = pymysql.connect(host=current_app.config['HOST'], user=current_app.config['USER'],
                             password=current_app.config['PASSWORD'], port=current_app.config['PORT'],
                             database=current_app.config['DATABASE'],
                             charset=current_app.config['CHARSET'])
        cursor = db.cursor()
        sql = "SELECT * FROM vuser WHERE email = '%s'" % (field.data)

        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is not None:
                raise ValidationError('电子邮箱已被注册')
        finally:
            db.close()


class LoginForm(Form):
    email = StringField(
        validators=[DataRequired(message="邮箱不能为空"), Length(8, 64, message="邮箱长度过短"), Email(message="电子邮箱不符合规范")])

    password = PasswordField(validators=[DataRequired(message="密码不可以为空，请输入你的密码")])


class EmailForm(Form):
    email = StringField(validators=[DataRequired(message="邮箱不能为空"), Length(8, 64, message="邮箱长度过短"), Email(message="电子邮箱不符合规范")])


class ResetPasswordForm(Form):
    password1 = PasswordField(validators=[DataRequired("密码不能为空"), EqualTo('password2', message='两次输入的密码不一致')])
    password2 = PasswordField(validators=[DataRequired("再次输入密码不能为空")])
