from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, validators, SelectMultipleField, \
    SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from flask_login import current_user
from ..models import SalesAreaHierarchy, DepartmentHierarchy, User, WebpageDescribe
from ..forms import BaseCsrfForm


def valid_sale_range(form, field):
    if form.user_type.data == "2" and field.data is None:
        raise validators.ValidationError('请选择销售范围')


def valid_dept_ranges(form, field):
    if form.user_type.data == "3" and field.data == []:
        raise validators.ValidationError('请选择所属部门')


def get_dynamic_sale_range_query(level_grade, parent_id=None):
    sahs = SalesAreaHierarchy.query.filter(SalesAreaHierarchy.level_grade == level_grade)
    if parent_id is not None:
        sahs = sahs.filter_by(parent_id=parent_id)

    return sahs.order_by(SalesAreaHierarchy.id).all()


def get_dynamic_dept_ranges_query():
    dhs = DepartmentHierarchy.query

    # 前端已进行控制,防止异常增加逻辑
    if current_user is None or not current_user.is_authenticated or current_user.departments.count() == 0:
        return dhs.order_by(DepartmentHierarchy.id).all()

    max_depart_level = current_user.get_max_level_grade()
    dhs = dhs.filter(DepartmentHierarchy.level_grade > max_depart_level)
    dhs = dhs.union(current_user.departments)

    return dhs.order_by(DepartmentHierarchy.id).all()


class BaseForm(Form):
    def reset_select_field(self):
        self.dept_ranges.query = get_dynamic_dept_ranges_query()
        self.sale_range_province.query = get_dynamic_sale_range_query(3)
        self.sale_range.query = get_dynamic_sale_range_query(4)

    @classmethod
    def get_sale_range_by_parent(cls, level_grade, parent_id):
        return get_dynamic_sale_range_query(level_grade, parent_id)


# BASE USER
class UserForm(BaseForm, BaseCsrfForm):
    email = StringField('邮箱', [validators.Email(message="请填写正确格式的email")])
    name = StringField('姓名', [validators.Length(min=2, max=30, message="字段长度必须大等于2小等于30")])
    nickname = StringField('昵称', [validators.Length(min=2, max=30, message="字段长度必须大等于2小等于30")])
    password = PasswordField('密码', validators=[
        validators.DataRequired(message="字段不可为空"),
        validators.Length(min=8, max=20, message="字段长度必须大等于8小等于20"),
        validators.EqualTo('password_confirm', message="两次输入密码不匹配")
    ])
    password_confirm = PasswordField('密码')
    address = TextAreaField('地址', [validators.Length(min=5, max=300, message="字段长度必须大等于5小等于300")])
    # 电话匹配规则 11位手机 or 3-4区号(可选)+7-8位固话+1-6分机号(可选)
    phone = StringField('电话',
                        [validators.Regexp(r'(^\d{11})$|(^(\d{3,4}-)?\d{7,8}(-\d{1,5})?$)', message="请输入正确格式的电话")])
    title = StringField('头衔')
    user_type = SelectField('用户类型', choices=[('3', '员工'), ('2', '经销商')],
                            validators=[validators.DataRequired(message="字段不可为空")])
    # dept_ranges = SelectMultipleField('dept_ranges',choices=[ ('-1','选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    # sale_range = SelectField('sale_range',choices=[ ('-1','选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=4).all() ])
    dept_ranges = QuerySelectMultipleField(u'所属部门', get_label="name", validators=[valid_dept_ranges])
    sale_range_province = QuerySelectField(u'销售范围(省)', get_label="name", allow_blank=True)
    sale_range = QuerySelectField(u'销售范围', get_label="name", allow_blank=True, validators=[valid_sale_range])
    join_dealer = SelectField(u'是否加盟', coerce=int, choices=[(1, '是'), (0, '否')])


# BASE USER_SEARCH
class UserSearchForm(BaseForm):
    email = StringField('邮箱')
    name = StringField('姓名')
    user_type = SelectField('用户类型', choices=[(3, '员工'), (2, '经销商')],
                            validators=[validators.DataRequired(message="字段不可为空")])
    # dept_ranges = SelectMultipleField('dept_ranges',choices=[ (-1,'选择所属部门')] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ])
    # sale_range = SelectField('sale_range',choices=[ (-1,'选择销售范围')] + [(str(sah.id),sah.name) for sah in SalesAreaHierarchy.query.filter_by(level_grade=3).all() ])
    dept_ranges = QuerySelectMultipleField(u'所属部门', get_label="name")
    sale_range_province = QuerySelectField(u'销售范围(省)', get_label="name", allow_blank=True)
    sale_range = QuerySelectField(u'销售范围', get_label="name", allow_blank=True)


class RegionalSearchForm(Form):
    regional = QuerySelectMultipleField(u'区域', get_label="name")

    def reset_select_field(self):
        self.regional.query = get_dynamic_sale_range_query(2)


class AuthoritySearchForm(BaseCsrfForm):
    roles = SelectMultipleField('角色', choices=[('', '全部')] + User.get_all_roles())
    web_types = SelectMultipleField('页面类型', choices=WebpageDescribe.get_all_types())
    describe = StringField('页面描述')
    submit = SubmitField('筛选条件')
