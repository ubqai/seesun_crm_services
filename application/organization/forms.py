from wtforms import Form, StringField, SelectField, SelectMultipleField,PasswordField,validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField,QuerySelectMultipleField
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
    #dept_ranges = SelectMultipleField('dept_ranges',choices=[ ('-1','选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    #sale_range = SelectField('sale_range',choices=[ ('-1','选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=4).all() ])
    dept_ranges = QuerySelectMultipleField(u'dept_ranges',query_factory=DepartmentHierarchy.get_dynamic_dept_ranges(),get_label="name")
    sale_range = QuerySelectField(u'sale_range', query_factory = SalesAreaHierarchy.get_dynamic_sale_range(),get_label="name",allow_blank=True)

    def valid_sale_range(self):
        if self.user_type.data=="2" and self.sale_range.data==None:
            self.sale_range.errors.append("请选择销售范围")
            return False
        return True
    def valid_dept_ranges(self):
        if self.user_type.data=="3" and self.dept_ranges.data==[]:
            self.dept_ranges.errors.append("请选择所属部门")
            return False
        return True

    def valid_select_field(self):
        return self.valid_sale_range() and self.valid_dept_ranges()

    def reset_select_field(self):
        self.sale_range.query = SalesAreaHierarchy.get_dynamic_sale_range()()
        self.dept_ranges.query = DepartmentHierarchy.get_dynamic_dept_ranges()()

#BASE USER_SEARCH
class UserSearchForm(Form):
    email = StringField('email')
    name = StringField('name')    
    user_type = SelectField('user_type',choices=[ (3,'员工'),(2,'经销商') ],validators=[validators.Required(message="字段不可为空")])
    #dept_ranges = SelectMultipleField('dept_ranges',choices=[ (-1,'选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    #sale_range = SelectField('sale_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])
    dept_ranges = QuerySelectMultipleField(u'dept_ranges',query_factory=DepartmentHierarchy.get_dynamic_dept_ranges(),get_label="name")
    sale_range = QuerySelectField(u'sale_range', query_factory = SalesAreaHierarchy.get_dynamic_sale_range(),get_label="name",allow_blank=True)

    def reset_select_field(self):
        self.sale_range.query = SalesAreaHierarchy.get_dynamic_sale_range()()
        self.dept_ranges.query = DepartmentHierarchy.get_dynamic_dept_ranges()()