from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
from . import app


# BASE CSRF FORM
class BaseCsrfForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = bytes(app.config['SECRET_KEY'], 'ascii')
        csrf_time_limit = timedelta(minutes=20)


class UserInfoForm(Form):
    email = StringField('email', [validators.Email(message="请填写正确格式的email")])
    name = StringField('name', [validators.Length(min=2, max=30, message="字段长度必须大等于2小等于30")])
    nickname = StringField('nickname', [validators.Length(min=2, max=30, message="字段长度必须大等于2小等于30")])
    password = PasswordField('password', validators=[
        validators.Required(message="字段不可为空"),
        validators.Length(min=8, max=20, message="字段长度必须大等于8小等于20"),
        validators.EqualTo('password_confirm', message="两次输入密码不匹配")
    ])
    password_confirm = PasswordField('re_password')
    address = TextAreaField('address', [validators.Length(min=5, max=300, message="字段长度必须大等于5小等于300")])
    # 电话匹配规则 11位手机 or 3-4区号(可选)+7-8位固话+1-6分机号(可选)
    phone = StringField('phone', [validators.Regexp(r'(^\d{11})$|(^(\d{3,4}-)?\d{7,8}(-\d{1,5})?$)', message="请输入正确格式的电话")])
    title = StringField('title')
    user_type = StringField('user_type')
    dept_ranges = StringField('dept_ranges')
    sale_range = StringField('sale_range')
