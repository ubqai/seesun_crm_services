# -*- coding: utf-8 -*-
import datetime
from app import db

# Contents_and_options: id, content_title_id, content_classification_option_id
contents_and_options = db.Table('contents_and_options',
	db.Column('id', db.Integer, primary_key = True),
	db.Column('content_title_id', db.Integer, db.ForeignKey('content_title.id')),
	db.Column('content_classification_option_id', db.Integer, db.ForeignKey('content_classification_option.id'))
	)

# Contents: id, content_title_id, name, description, content_image_links(json), content_detail_link
class Content(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	description = db.Column(db.Text)
	image_links = db.Column(db.JSON)
	detail_link = db.Column(db.String(200))
	created_at  = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at  = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	title_id = db.Column(db.Integer, db.ForeignKey('content_title.id'))

	def __repr__(self):
		return '<Content: %s>' % self.name

# Content_titles: id, name,description,content_thumbnail,reference_info(json{name,value})
class ContentTitle(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	description = db.Column(db.Text)
	content_thumbnail = db.Column(db.String(100))
	reference_info = db.Column(db.JSON)
	created_at  = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at  = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	contents = db.relationship('Content', backref = 'title', lazy = 'dynamic')
	options = db.relationship('ContentClassificationOption', 
		secondary = contents_and_options,
		backref = db.backref('titles', lazy = 'dynamic'))

	def __repr__(self):
		return '<ContentTitle: %s>' % self.name

	def append_options(self, options):
		existing_options = self.options
		new_options = []
		for option in options:
			if not option in existing_options:
				new_options.append(option)
		for option in new_options:
			existing_options.append(option)
		return self.options

	def update_options(self, options):
		self.options = []
		self.append_options(options)
		return self.options

# Content_categories: id,name
class ContentCategory(db.Model):
	id         = db.Column(db.Integer, primary_key = True)
	name       = db.Column(db.String(100), unique = True)
	created_at = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	classifications = db.relationship('ContentClassification', backref = 'category', lazy = 'dynamic')

	def __repr__(self):
		return '<ContentCategory: %s>' % self.name

# Content_classifications: id, content_category_id, name,description
class ContentClassification(db.Model):
	id          = db.Column(db.Integer, primary_key = True)
	name        = db.Column(db.String(100))
	description = db.Column(db.Text)
	created_at  = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at  = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	category_id = db.Column(db.Integer, db.ForeignKey('content_category.id'))
	options     = db.relationship('ContentClassificationOption', backref = 'classification', lazy = 'dynamic')

	def __repr__(self):
		return '<ContentClassification: %s>' % self.name

# Content_classification_options: id, content_classification_id,name
class ContentClassificationOption(db.Model):
	id         = db.Column(db.Integer, primary_key = True)
	name       = db.Column(db.String(100))
	created_at = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	classification_id = db.Column(db.Integer, db.ForeignKey('content_classification.id'))

	def __repr__(self):
		return '<ContentClassificationOption: %s>' % self.name


