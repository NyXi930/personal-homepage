from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User  

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(3, 64, message='用户名长度需在3-64位之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(6, 128, message='密码长度需在6-128位之间'),
        EqualTo('confirm_password', message='两次输入的密码必须一致')
    ])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册，请更换')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class NameForm(FlaskForm):
    id = IntegerField('Student ID', validators=[DataRequired()])
    name = StringField('Student Name', validators=[DataRequired()])
    major = SelectField('Major', coerce=int)
    submit = SubmitField('Submit')

class EditForm(NameForm):
    submit = SubmitField("Edit")