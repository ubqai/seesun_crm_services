from wtforms import Form, StringField, SelectField, SelectMultipleField,PasswordField,validators
from ..models import *


#BASE USER_LOGIN
class UserLoginForm(Form):
    email = StringField('email',[validators.Email(message="请填写正确格式的email")])
    password = PasswordField('password', validators=[
        validators.Length(min=8,max=20,message="字段长度必须大等于8小等于20"),
    ])
    
#BASE USER
class UserForm(Form):
    email = StringField('email',[validators.Email(message="请填写正确格式的email")])
    name = StringField('name',[validators.Length(min=2,max=30,message="字段长度必须大等于2小等于30")])
    nickname = StringField('nickname',[validators.Length(min=2,max=30,message="字段长度必须大等于2小等于30")])
    password = PasswordField('password', validators=[
        validators.Required(message="字段不可为空"),
        validators.Length(min=8,max=20,message="字段长度必须大等于8小等于20"),
        validators.EqualTo('password_confirm', message="两次输入密码不匹配")
    ])
    password_confirm = PasswordField('re_password')
    address = StringField('address',[validators.Length(min=5,max=300,message="字段长度必须大等于5小等于300")])
    #电话匹配规则 11位手机 or 3-4区号(可选)+7-8位固话+1-6分机号(可选)
    phone = StringField('phone',[validators.Regexp(r'(^\d{11})$|(^(\d{3,4}-)?\d{7,8}(-\d{1,5})?$)',message="请输入正确格式的电话")])
    title = StringField('title')
    user_type = SelectField('user_type',choices=[ ('3','员工'),('2','经销商') ],validators=[validators.Required(message="字段不可为空")])
    dept_ranges = SelectMultipleField('dept_ranges',choices=[ ('-1','选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    sale_range = SelectField('sale_range',choices=[ ('-1','选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=4).all() ])

#BASE USER_SEARCH
class UserSearchForm(Form):
    email = StringField('email')
    name = StringField('name')    
    user_type = SelectField('user_type',choices=[ (3,'员工'),(2,'经销商') ],validators=[validators.Required(message="字段不可为空")])
    dept_ranges = SelectMultipleField('dept_ranges',choices=[ (-1,'选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    sale_range = SelectField('sale_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])
