# -*- coding: utf-8 -*-
import wtforms
from wtforms.validators import *
from ..models import User


class ContentForm(wtforms.Form):
    name = wtforms.StringField('内容标题',  validators=[DataRequired(message='name is necessary')])
    description = wtforms.TextAreaField('内容描述', validators=[DataRequired(message='description is necessary')])

    def save(self, content):
        self.populate_obj(content)
        return content


class ContentCategoryForm(wtforms.Form):
    name = wtforms.StringField('目录名称', validators=[DataRequired(message='name is necessary')])

    def save(self, category):
        self.populate_obj(category)
        return category


class ContentClassificationForm(wtforms.Form):
    name = wtforms.StringField('次级目录名称', validators=[DataRequired(message='name is necessary')])
    description = wtforms.TextAreaField('次级目录描述', validators=[DataRequired(message='description is necessary')])

    def save(self, classification):
        self.populate_obj(classification)
        return classification


class ContentClassificationOptionForm(wtforms.Form):
    name = wtforms.StringField('三级目录名称', validators=[DataRequired(message='option name is necessary')])

    def save(self, option):
        self.populate_obj(option)
        return option


class MaterialForm(wtforms.Form):
    name = wtforms.StringField('物料名称', validators=[DataRequired(message='material name is necessary')])

    def save(self, obj):
        self.populate_obj(obj)
        return obj


class MaterialApplicationForm(wtforms.Form):
    # delete '等待经销商再次确认', '经销商已确认', '已取消'
    status = wtforms.SelectField(
        '审核意见',
        choices=[('同意申请', '同意申请'), ('拒绝申请', '拒绝申请')],
        validators=[DataRequired(message='status is necessary')])
    memo = wtforms.TextAreaField('审核备注')

    def save(self, obj):
        self.populate_obj(obj)
        return obj


class MaterialApplicationSearchForm(wtforms.Form):
    created_at_gt = wtforms.StringField('申请时间从')
    created_at_lt = wtforms.StringField('到')
    app_no = wtforms.StringField('申请号')
    dealer = wtforms.SelectField(
        '经销商',
        choices=[('', '')] + [(user.id, user.nickname) for user in User.query.filter(User.user_or_origin == 2)]
    )
    status = wtforms.SelectField(
        '申请状态',
        choices=[('', ''), ('新申请', '新申请'), ('同意申请', '同意申请'), ('拒绝申请', '拒绝申请'), ('已完成', '已完成')]
    )

