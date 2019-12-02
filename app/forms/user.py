from wtforms import Form, StringField, RadioField, DateField
from wtforms.validators import DataRequired, Length


class UserForm(Form):
    nickname = StringField(validators=[DataRequired(message="昵称不能为空"), Length(2, 10, message='昵称至少需要两个字符，最多10个字符')])
    motto = StringField(validators=[Length(0, 100, message='座右铭最多100个字符')])
    info = StringField(validators=[Length(0, 1000, message='用户简介最多1000个字符')])
    birthday = DateField('Birthday', format='%Y-%m-%d')
    gender = RadioField('Gender', choices=[('1', 'Male'), ('0', 'Female')])

class birthdayForm(Form):
    birthday = DateField('Birthday', format='%Y-%m-%d')

class genderForm(Form):
    gender = RadioField('Gender', choices=[('1', 'Male'), ('0', 'Female')])