# -*- coding: utf-8 -*-
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

from app     import app, db
from helpers import object_list
from models  import Content, ContentTitle, ContentCategory, ContentClassification, ContentClassificationOption
from content.forms import *

content = Blueprint('content', __name__, template_folder = 'templates')
# url -- /content/..
@content.route('/')
def index():
	return render_template('content/index.html')

@content.route('/new/<title_id>', methods = ['GET', 'POST'])
def new(title_id):
	if request.method == 'POST':
		form = ContentForm(request.form)
		if form.validate():
			content = form.save(Content(title_id = title_id))
			db.session.add(content)
			db.session.commit()
			flash('Content "{name}" created successfully.'.format(name = content.name), 'success')
			return redirect(url_for('content.title_show', id = title_id))
	else:
		form = ContentForm()
	return render_template('content/new.html', form = form, title_id = title_id)

@content.route('/<id>')
def show(id):
	content = Content.query.get_or_404(id)
	return render_template('content/show.html', content = content)

@content.route('/<id>/edit', methods = ['GET', 'POST'])
def edit(id):
	content = Content.query.get_or_404(id)
	if request.method == 'POST':
		form = ContentForm(request.form)
		if form.validate():
			content = form.save(content)
			db.session.add(content)
			db.session.commit()
			flash('Content "{name}" has been updated.'.format(name = content.name), 'success')
			return redirect(url_for('content.title_show', id = content.title_id))
	else:
		form = ContentForm(obj = content)
	return render_template('content/edit.html', form = form, content = content)

@content.route('/<id>/delete', methods = ['GET', 'POST'])
def delete(id):
	content = Content.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(content)
		db.session.commit()
		flash('Content "{name}" has been deleted.'.format(name = content.name), 'success')
		return redirect(url_for('content.title_show', id = content.title_id))
	return render_template('content/delete.html', content = content)

# url -- /content/title/..
@content.route('/title/index')
def title_index():
	titles = ContentTitle.query.order_by(ContentTitle.created_at.desc())
	return render_template('content/title/index.html', titles = titles)

@content.route('/title/new', methods = ['GET', 'POST'])
def title_new():
	options = ContentClassificationOption.query.order_by(ContentClassificationOption.classification_id)
	if request.method == 'POST':
		form = ContentTitleForm(request.form)
		if form.validate():
			option_ids = request.form.getlist('option_ids[]')
			request_options = ContentClassificationOption.query.filter(ContentClassificationOption.id.in_(option_ids))
			title = form.save(ContentTitle())
			title.append_options(request_options)
			db.session.add(title)
			db.session.commit()
			flash('Content title "{name}" created successfully.'.format(name = title.name), 'success')
			return redirect(url_for('content.title_index'))
	else:
		form = ContentTitleForm()
	return render_template('content/title/new.html', form = form, options = options)

@content.route('/title/<id>')
def title_show(id):
	title = ContentTitle.query.get_or_404(id)
	return render_template('content/title/show.html', title = title)

@content.route('/title/<id>/edit', methods = ['GET', 'POST'])
def title_edit(id):
	options = ContentClassificationOption.query.order_by(ContentClassificationOption.classification_id)
	title = ContentTitle.query.get_or_404(id)
	if request.method == 'POST':
		form = ContentTitleForm(request.form)
		if form.validate():
			option_ids = request.form.getlist('option_ids[]')
			request_options = ContentClassificationOption.query.filter(ContentClassificationOption.id.in_(option_ids))
			title = form.save(title)
			title.update_options(request_options)
			db.session.add(title)
			db.session.commit()
			flash('Content title "{name}" has been updated.'.format(name = title.name), 'success')
			return redirect(url_for('content.title_index'))
	else:
		form = ContentTitleForm(obj = title)
	return render_template('content/title/edit.html', form = form, title = title, options = options)

@content.route('/title/<id>/delete', methods = ['GET', 'POST'])
def title_delete(id):
	title = ContentTitle.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(title)
		db.session.commit()
		flash('Content title "{name}" has been deleted.'.format(name = title.name), 'success')
		return redirect(url_for('content.title_index'))
	return render_template('content/title/delete.html', title = title)

# url -- /content/category/..
@content.route('/category/index')
def category_index():
	categories = ContentCategory.query.order_by(ContentCategory.created_at.asc())
	return render_template('content/category/index.html', categories = categories)

@content.route('/category/new', methods = ['GET', 'POST'])
def category_new():
	if request.method == 'POST':
		form = ContentCategoryForm(request.form)
		if form.validate():
			category = form.save(ContentCategory())
			db.session.add(category)
			db.session.commit()
			flash('Content category "{name}" created successfully.'.format(name = category.name), 'success')
			return redirect(url_for('content.category_index'))
	else:
		form = ContentCategoryForm()
	return render_template('content/category/new.html', form = form)

@content.route('/category/<id>')
def category_show(id):
	category = ContentCategory.query.get_or_404(id)
	return render_template('content/category/show.html', category = category)

@content.route('/category/<id>/edit', methods = ['GET', 'POST'])
def category_edit(id):
	category = ContentCategory.query.get_or_404(id)
	if request.method == 'POST':
		form = ContentCategoryForm(request.form)
		if form.validate():
			category = form.save(category)
			db.session.add(category)
			db.session.commit()
			flash('Content category "{name}" has been updated.'.format(name = category.name), 'success')
			return redirect(url_for('content.category_index'))
	else:
		form = ContentCategoryForm(obj = category)
	return render_template('content/category/edit.html', form = form, category = category)

@content.route('/category/<id>/delete', methods = ['GET', 'POST'])
def category_delete(id):
	category = ContentCategory.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(category)
		db.session.commit()
		flash('Content category "{name}" has been deleted.'.format(name = category.name), 'success')
		return redirect(url_for('content.category_index'))
	return render_template('content/category/delete.html', category = category)

# url -- /content/classification/..
@content.route('/classification/new/<category_id>', methods = ['GET', 'POST'])
def classification_new(category_id):
	if request.method == 'POST':
		form = ContentClassificationForm(request.form)
		if form.validate():
			classification = form.save(ContentClassification(category_id = category_id))
			db.session.add(classification)
			db.session.commit()
			flash('Content classification "{name}" created successfully.'.format(name = classification.name), 'success')
			return redirect(url_for('content.category_show', id = category_id))
	else:
		form = ContentClassificationForm()
	return render_template('content/classification/new.html', form = form, category_id = category_id)

@content.route('/classification/<id>')
def classification_show(id):
	classification = ContentClassification.query.get_or_404(id)
	return render_template('content/classification/show.html', classification = classification)

@content.route('/classification/<id>/edit', methods = ['GET', 'POST'])
def classification_edit(id):
	classification = ContentClassification.query.get_or_404(id)
	if request.method == 'POST':
		form = ContentClassificationForm(request.form)
		if form.validate():
			classification = form.save(classification)
			db.session.add(classification)
			db.session.commit()
			flash('Content Classification "{name}" has been updated.'.format(name = classification.name), 'success')
			return redirect(url_for('content.category_show', id = classification.category_id))
	else:
		form = ContentClassificationForm(obj = classification)
	return render_template('content/classification/edit.html', form = form, classification = classification)

@content.route('/classification/<id>/delete', methods = ['GET', 'POST'])
def classification_delete(id):
	classification = ContentClassification.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(classification)
		db.session.commit()
		flash('Content classification "{name}" has been deleted.'.format(name = classification.name), 'success')
		return redirect(url_for('content.category_show', id = classification.category_id))
	return render_template('content/classification/delete.html', classification = classification)

# url -- /content/option/..
@content.route('/option/new/<classification_id>', methods = ['GET', 'POST'])
def option_new(classification_id):
	if request.method == 'POST':
		form = ContentClassificationOptionForm(request.form)
		if form.validate():
			option = form.save(ContentClassificationOption(classification_id = classification_id))
			db.session.add(option)
			db.session.commit()
			flash('Content classification Option "{name}" created successfully.'.format(name = option.name), 'success')
			return redirect(url_for('content.classification_show', id = classification_id))
	else:
		form = ContentClassificationOptionForm()
	return render_template('content/option/new.html', form = form, classification_id = classification_id)

@content.route('/option/<id>')
def option_show(id):
	option = ContentClassificationOption.query.get_or_404(id)
	return render_template('content/option/show.html', option = option)

@content.route('/option/<id>/edit', methods = ['GET', 'POST'])
def option_edit(id):
	option = ContentClassificationOption.query.get_or_404(id)
	if request.method == 'POST':
		form = ContentClassificationOptionForm(request.form)
		if form.validate():
			option = form.save(option)
			db.session.add(option)
			db.session.commit()
			flash('Content Classification Option "{name}" has been updated.'.format(name = option.name), 'success')
			return redirect(url_for('content.classification_show', id = option.classification_id))
	else:
		form = ContentClassificationOptionForm(obj = option)
	return render_template('content/option/edit.html', form = form, option = option)

@content.route('/option/<id>/delete', methods = ['GET', 'POST'])
def option_delete(id):
	option = ContentClassificationOption.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(option)
		db.session.commit()
		flash('Content classification option "{name}" has been deleted.'.format(name = option.name), 'success')
		return redirect(url_for('content.classification_show', id = option.classification_id))
	return render_template('content/option/delete.html', option = option)

