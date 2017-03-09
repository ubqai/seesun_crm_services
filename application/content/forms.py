# -*- coding: utf-8 -*-
import wtforms
from wtforms.validators import *

from ..models import Content, ContentCategory, ContentClassification, ContentClassificationOption

class ContentForm(wtforms.Form):
    name = wtforms.StringField('内容标题',  validators = [DataRequired(message = 'name is necessary')])
    description = wtforms.TextAreaField('内容描述', validators= [DataRequired(message = 'description is necessary')])

    def save(self, content):
        self.populate_obj(content)
        return content

class ContentCategoryForm(wtforms.Form):
    name = wtforms.StringField('目录名称', validators = [DataRequired(message = 'name is necessary')])

    def save(self, category):
        self.populate_obj(category)
        return category

class ContentClassificationForm(wtforms.Form):
    name = wtforms.StringField('次级目录名称',  validators = [DataRequired(message = 'name is necessary')])
    description = wtforms.TextAreaField('次级目录描述', validators= [DataRequired(message = 'description is necessary')])

    def save(self, classification):
        self.populate_obj(classification)
        return classification

class ContentClassificationOptionForm(wtforms.Form):
    name = wtforms.StringField('三级目录名称', validators = [DataRequired(message = 'option name is necessary')])

    def save(self, option):
        self.populate_obj(option)
        return option

class MaterialForm(wtforms.Form):
    name = wtforms.StringField('物料名称', validators = [DataRequired(message = 'material name is necessary')])

    def save(self, obj):
        self.populate_obj(obj)
        return obj