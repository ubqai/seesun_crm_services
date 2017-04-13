from wtforms import StringField, PasswordField, validators, TextAreaField, BooleanField
from ..forms import BaseCsrfForm


# BASE ACCOUNT_LOGIN
class AccountLoginForm(BaseCsrfForm):
    email = StringField('邮箱', [validators.Email(message="请填写正确格式的email")])
    password = PasswordField('密码', validators=[
        validators.Length(min=8, max=20, message="字段长度必须大等于8小等于20"),
    ])
    remember_me = BooleanField('记住我')


# WECHAT USER_LOGIN
class WechatUserLoginForm(AccountLoginForm):
    openid = StringField('微信openId', [validators.DataRequired()])


# BASE USER
class AccountForm(BaseCsrfForm):
    email = StringField('邮箱', [validators.Email(message="请填写正确格式的email")])
    name = StringField('姓名', default="", validators=[validators.Length(min=2, max=30, message="字段长度必须大等于2小等于30")])
    nickname = StringField('昵称', default="", validators=[validators.Length(min=2, max=30, message="字段长度必须大等于2小等于30")])
    password = PasswordField('密码', validators=[
        validators.DataRequired(message="字段不可为空"),
        validators.Length(min=8, max=20, message="字段长度必须大等于8小等于20"),
        validators.EqualTo('password_confirm', message="两次输入密码不匹配")
    ])
    password_confirm = PasswordField('密码')
    address = TextAreaField('地址', default="",
                            validators=[validators.Length(min=5, max=300, message="字段长度必须大等于5小等于300")])
    # 电话匹配规则 11位手机 or 3-4区号(可选)+7-8位固话+1-6分机号(可选)
    phone = StringField('电话', default="",
                        validators=[
                            validators.Regexp(r'(^\d{11})$|(^(\d{3,4}-)?\d{7,8}(-\d{1,5})?$)', message="请输入正确格式的电话")])
    title = StringField('头衔', default="")
    user_type = StringField('用户类型', validators=[validators.AnyOf(['员工', '经销商'], message="字段枚举错误")])
    dept_ranges = StringField(u'所属部门', default="")
    sale_range = StringField(u'销售范围', default="")
