# -*- coding: utf-8 -*-
import datetime
from app import db

class Rails(object):
	@property
	def save(self):
		db.session.add(self)
		db.session.commit()
		return self

	@property
	def delete(self):
		db.session.delete(self)
		db.session.commit()
		return self

# Contents_and_options: id, content_title_id, content_classification_option_id
contents_and_options = db.Table('contents_and_options',
	db.Column('id', db.Integer, primary_key = True),
	db.Column('content_title_id', db.Integer, db.ForeignKey('content_title.id')),
	db.Column('content_classification_option_id', db.Integer, db.ForeignKey('content_classification_option.id'))
	)

# Contents: id, content_title_id, name, description, content_image_links(json), content_detail_link
class Content(db.Model, Rails):
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

	@property
	def image_path(self):
		return '/static/images/sport2.jpg'

# Content_titles: id, name,description,content_thumbnail,reference_info(json{name,value})
class ContentTitle(db.Model, Rails):
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

	@property
	def delete_p(self):
		for content in self.contents:
			content.delete
		self.delete
		return self

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

	# temporarily used for development
	@property
	def image_path(self):
		return '/static/images/sport1.jpg'

# Content_categories: id,name
class ContentCategory(db.Model, Rails):
	id         = db.Column(db.Integer, primary_key = True)
	name       = db.Column(db.String(100), unique = True)
	created_at = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	classifications = db.relationship('ContentClassification', backref = 'category', lazy = 'dynamic')

	def __repr__(self):
		return '<ContentCategory: %s>' % self.name

	@property
	def delete_p(self):
		for classification in self.classifications:
			classification.delete_p
		self.delete
		return self

# Content_classifications: id, content_category_id, name,description
class ContentClassification(db.Model, Rails):
	id          = db.Column(db.Integer, primary_key = True)
	name        = db.Column(db.String(100))
	description = db.Column(db.Text)
	created_at  = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at  = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	category_id = db.Column(db.Integer, db.ForeignKey('content_category.id'))
	options     = db.relationship('ContentClassificationOption', backref = 'classification', lazy = 'dynamic')

	def __repr__(self):
		return '<ContentClassification: %s>' % self.name

	@property
	def delete_p(self):
		for option in self.options:
			option.delete
		self.delete
		return self

# Content_classification_options: id, content_classification_id,name
class ContentClassificationOption(db.Model, Rails):
	id         = db.Column(db.Integer, primary_key = True)
	name       = db.Column(db.String(100))
	created_at = db.Column(db.DateTime, default = datetime.datetime.now)
	updated_at = db.Column(db.DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)

	classification_id = db.Column(db.Integer, db.ForeignKey('content_classification.id'))

	def __repr__(self):
		return '<ContentClassificationOption: %s>' % self.name


