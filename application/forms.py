from wtforms import Form, StringField, SelectField, SelectMultipleField, validators
from .models import *

# http://blog.csdn.net/u010605509/article/details/43456683
def check_radio_choose(form,field):
    if field.data=="" or field.data=="none":
        raise "please choose %s" % (field.name)

#BASE USER
class UserForm(Form):
    email = StringField('email',[validators.Email()])
    name = StringField('name',[validators.Length(min=2,max=30)])
    nickname = StringField('nickname',[validators.Length(min=2,max=30)])
    address = StringField('address',[validators.Length(min=5)])
    phone = StringField('phone',[validators.Length(min=11,max=15)])
    title = StringField('title')

class UserStaffForm(UserForm):
    # int型 校验时会出错，因此作为默认提示选项
    dept_range = SelectField('dept_range',choices=[ (-1,'选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])

class UserDealerForm(UserForm):
    # int型 校验时会出错，因此作为默认提示选项
    existed_sales_range=StringField('existed_sales_range')
    sales_range = SelectMultipleField('sales_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])


#BASE USERSEARCH
class UserSearchForm(Form):
    email = StringField('email')
    name = StringField('name')    

class UserStaffSearchForm(UserSearchForm):
    dept_range = SelectField('dept_range',choices=[ ('-1','选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])

class UserDealerSearchForm(UserSearchForm):
    sales_range = SelectMultipleField('sales_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])