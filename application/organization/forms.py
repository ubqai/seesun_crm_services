from wtforms import Form, StringField, TextAreaField,SelectField, SelectMultipleField,PasswordField,validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField,QuerySelectMultipleField
from ..models import *
from flask_login import *


#CUSTOM  VALIDATORS
def valid_sale_range(form, field):
    if form.user_type.data=="2" and form.sale_range.data==None:
        raise validators.ValidationError('请选择销售范围')


def valid_dept_ranges(form, field):
    if form.user_type.data=="3" and form.dept_ranges.data==[]:
        raise validators.ValidationError('请选择所属部门')      



def get_dynamic_sale_range_query(level_grade,parent_id=None):
    sahs = SalesAreaHierarchy.query.filter_by(level_grade=level_grade)
    if not parent_id==None:
        sahs = sahs.filter_by(parent_id=parent_id)

    return sahs.order_by(SalesAreaHierarchy.id).all()


def get_dynamic_dept_ranges_query():
    dhs = DepartmentHierarchy.query
    if current_user==None or not current_user.is_active or current_user.user_or_origin==2:
        return dhs.order_by(DepartmentHierarchy.id).all()

    max_depart_level = current_user.get_max_level_grade()
    dhs = dhs.filter(DepartmentHierarchy.level_grade>max_depart_level)
    dhs = dhs.union(current_user.departments)

    return dhs.order_by(DepartmentHierarchy.id).all()

#BASE USER_LOGIN
class UserLoginForm(Form):
    email = StringField('email',[validators.Email(message="请填写正确格式的email")])
    password = PasswordField('password', validators=[
        validators.Length(min=8,max=20,message="字段长度必须大等于8小等于20"),
    ])

class BaseForm(Form):
    def reset_select_field(self):
        self.dept_ranges.query = get_dynamic_dept_ranges_query()
        self.sale_range_province.query = get_dynamic_sale_range_query(3)
        self.sale_range.query = get_dynamic_sale_range_query(4)

    @classmethod
    def get_sale_range_by_parent(cls,level_grade,parent_id):
        return get_dynamic_sale_range_query(level_grade,parent_id)


#BASE USER
class UserForm(BaseForm):
    email = StringField('email',[validators.Email(message="请填写正确格式的email")])
    name = StringField('name',[validators.Length(min=2,max=30,message="字段长度必须大等于2小等于30")])
    nickname = StringField('nickname',[validators.Length(min=2,max=30,message="字段长度必须大等于2小等于30")])
    password = PasswordField('password', validators=[
        validators.Required(message="字段不可为空"),
        validators.Length(min=8,max=20,message="字段长度必须大等于8小等于20"),
        validators.EqualTo('password_confirm', message="两次输入密码不匹配")
    ])
    password_confirm = PasswordField('re_password')
    address = TextAreaField('address',[validators.Length(min=5,max=300,message="字段长度必须大等于5小等于300")])
    #电话匹配规则 11位手机 or 3-4区号(可选)+7-8位固话+1-6分机号(可选)
    phone = StringField('phone',[validators.Regexp(r'(^\d{11})$|(^(\d{3,4}-)?\d{7,8}(-\d{1,5})?$)',message="请输入正确格式的电话")])
    title = StringField('title')
    user_type = SelectField('user_type',choices=[ ('3','员工'),('2','经销商') ],validators=[validators.Required(message="字段不可为空")])
    #dept_ranges = SelectMultipleField('dept_ranges',choices=[ ('-1','选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    #sale_range = SelectField('sale_range',choices=[ ('-1','选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=4).all() ])
    dept_ranges = QuerySelectMultipleField(u'dept_ranges',get_label="name",validators=[valid_dept_ranges])
    sale_range_province = QuerySelectField(u'sale_range_province', get_label="name",allow_blank=True)
    sale_range = QuerySelectField(u'sale_range', get_label="name",allow_blank=True,validators=[valid_sale_range])

#BASE USER_SEARCH
class UserSearchForm(BaseForm):
    email = StringField('email')
    name = StringField('name')    
    user_type = SelectField('user_type',choices=[ (3,'员工'),(2,'经销商') ],validators=[validators.Required(message="字段不可为空")])
    #dept_ranges = SelectMultipleField('dept_ranges',choices=[ (-1,'选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    #sale_range = SelectField('sale_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])
    dept_ranges = QuerySelectMultipleField(u'dept_ranges',get_label="name")
    sale_range_province = QuerySelectField(u'sale_range_province', get_label="name",allow_blank=True)
    sale_range = QuerySelectField(u'sale_range', get_label="name",allow_blank=True)