from wtforms import Form, StringField, SelectField, SelectMultipleField,PasswordField,validators
from ..models import *


#BASE USER
class UserForm(Form):
    email = StringField('email',[validators.Email()])
    name = StringField('name',[validators.Length(min=2,max=30)])
    nickname = StringField('nickname',[validators.Length(min=2,max=30)])
    password = PasswordField('password', validators=[
        validators.Required(),
        validators.EqualTo('password_confirm', message='Passwords must match')
    ])
    password_confirm = PasswordField('re_password')
    address = StringField('address',[validators.Length(min=5)])
    phone = StringField('phone',[validators.Length(min=11,max=15)])
    title = StringField('title')
    user_type = SelectField('user_type',choices=[ ('3','员工'),('2','经销商') ],validators=[validators.Required()])
    dept_ranges = SelectMultipleField('dept_ranges',choices=[ ('-1','选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    sale_range = SelectField('sale_range',choices=[ ('-1','选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=4).all() ])

#BASE USERSEARCH
class UserSearchForm(Form):
    email = StringField('email')
    name = StringField('name')    
    user_type = SelectField('user_type',choices=[ (3,'员工'),(2,'经销商') ],validators=[validators.Required()])
    dept_ranges = SelectMultipleField('dept_ranges',choices=[ (-1,'选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    sale_range = SelectField('sale_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])
