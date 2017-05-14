# -*- coding: utf-8 -*-
from wtforms import Form, StringField, TextAreaField, SelectField
from wtforms.validators import *
from ..models import User, SalesAreaHierarchy


class ContentForm(Form):
    name = StringField('内容标题',  validators=[DataRequired(message='name is necessary')])
    description = TextAreaField('内容描述', validators=[DataRequired(message='description is necessary')])

    def save(self, content):
        self.populate_obj(content)
        return content


class ContentCategoryForm(Form):
    name = StringField('目录名称', validators=[DataRequired(message='name is necessary')])

    def save(self, category):
        self.populate_obj(category)
        return category


class ContentClassificationForm(Form):
    name = StringField('次级目录名称', validators=[DataRequired(message='name is necessary')])
    description = TextAreaField('次级目录描述', validators=[DataRequired(message='description is necessary')])

    def save(self, classification):
        self.populate_obj(classification)
        return classification


class ContentClassificationOptionForm(Form):
    name = StringField('三级目录名称', validators=[DataRequired(message='option name is necessary')])

    def save(self, option):
        self.populate_obj(option)
        return option


class MaterialForm(Form):
    name = StringField('物料名称', validators=[DataRequired(message='物料名称必填')])
    stock_num = StringField('库存数量', validators=[DataRequired(message='库存数量必填')])

    def save(self, obj):
        self.populate_obj(obj)
        return obj


class MaterialApplicationForm(Form):
    # delete '等待经销商再次确认', '经销商已确认', '已取消'
    status = SelectField(
        '审核意见',
        choices=[('同意申请', '同意申请'), ('拒绝申请', '拒绝申请')],
        validators=[DataRequired(message='status is necessary')])
    memo = TextAreaField('审核备注')

    def save(self, obj):
        self.populate_obj(obj)
        return obj


def get_provinces():
    return SalesAreaHierarchy.query.filter(SalesAreaHierarchy.level_grade == 3).order_by(SalesAreaHierarchy.id)


# 后台员工申请表单
class MaterialApplicationForm2(Form):
    department = StringField('申请部门')
    applicant = StringField('申请人')
    application_date = StringField('申请日期')
    customer = StringField('客户名称')
    sales_area = SelectField('销售区域*', choices=[('', '')] + [(obj.name, obj.name) for obj in get_provinces()])
    project_name = StringField('项目名称')
    purpose = StringField('申请用途*')
    app_memo = TextAreaField('申请备注')
    delivery_method = StringField('寄件方式*')
    receive_address = StringField('收件地址*')
    receiver = StringField('收件人*')
    receiver_tel = StringField('收件人电话*')


class MaterialApplicationSearchForm(Form):
    created_at_gt = StringField('申请时间从')
    created_at_lt = StringField('到')
    app_no = StringField('申请号')
    # dealer = SelectField(
    #     '经销商',
    #    choices=[('', '')] + [(user.id, user.nickname) for user in User.query.filter(User.user_or_origin == 2)]
    # )
    sales_area = SelectField('销售区域(省份)', choices=[('', '')] + [(obj.name, obj.name) for obj in get_provinces()])
    status = SelectField(
        '申请状态',
        choices=[('', ''), ('新申请', '新申请'), ('同意申请', '同意申请'), ('拒绝申请', '拒绝申请'), ('已完成', '已完成')]
    )
    app_type = SelectField('类型', choices=[('', ''), (2, '经销商申请'), (3, '员工申请')])


class LogisticsCompanyInfoForm(Form):
    name = StringField('名称', validators=[DataRequired()])
    telephone = StringField('电话', validators=[DataRequired()])

    def save(self, obj):
        self.populate_obj(obj)
        return obj


