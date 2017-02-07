# -*- coding: utf-8 -*-
import wtforms
from wtforms.validators import *

from models import Content, ContentTitle, ContentCategory, ContentClassification, ContentClassificationOption

class ContentForm(wtforms.Form):
	name = wtforms.StringField('Content Name',  validators = [DataRequired(message = 'name is necessary')])
	description = wtforms.TextAreaField('Description', validators= [DataRequired(message = 'description is necessary')])

	def save(self, content):
		self.populate_obj(content)
		return content

class ContentTitleForm(wtforms.Form):
	name = wtforms.StringField('Title Name', validators = [DataRequired(message = 'title name is necessary')])
	content_thumbnail = wtforms.StringField('Content Thumbnail', validators = [DataRequired(message = 'content thumbnail is necessary')])
	description = wtforms.TextAreaField('Description', validators = [DataRequired(message = 'description is necessary')])

	def save(self, title):
		self.populate_obj(title)
		return title

class ContentCategoryForm(wtforms.Form):
	name = wtforms.StringField('Category Name', validators = [DataRequired(message = 'name is necessary')])

	def save(self, category):
		self.populate_obj(category)
		return category

class ContentClassificationForm(wtforms.Form):
	name = wtforms.StringField('Classification Name',  validators = [DataRequired(message = 'name is necessary')])
	description = wtforms.TextAreaField('Description', validators= [DataRequired(message = 'description is necessary')])

	def save(self, classification):
		self.populate_obj(classification)
		return classification

class ContentClassificationOptionForm(wtforms.Form):
	name = wtforms.StringField('Option Name', validators = [DataRequired(message = 'option name is necessary')])

	def save(self, option):
		self.populate_obj(option)
		return option