# -*- coding: utf-8 -*-
import os
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

from ..     import app, db
from ..helpers import object_list, save_upload_file, delete_file, clip_image
from ..models  import Content, ContentCategory, ContentClassification, ContentClassificationOption, MaterialApplication, Material
from .forms    import *

content = Blueprint('content', __name__, template_folder = 'templates')
content_image_size = (379, 226)

# url -- /content/..
@content.route('/')
def root():
    return redirect(url_for('content.index'))

@content.route('/index/<int:category_id>/')
def index(category_id):
    category = ContentCategory.query.get_or_404(category_id)
    contents = Content.query.filter(Content.category_id == category_id).order_by(Content.created_at.desc())
    return object_list('content/index.html', contents, paginate_by = 2, category = category)

@content.route('/new/<int:category_id>', methods = ['GET', 'POST'])
def new(category_id):
    if request.method == 'POST':
        form = ContentForm(request.form)
        if form.validate():
            option_ids = request.form.getlist('option_ids[]') 
            request_options = ContentClassificationOption.query.filter(ContentClassificationOption.id.in_(option_ids))
            content = form.save(Content(category_id = category_id))
            content.append_options(request_options)
            image_links = []
            if request.files:
                for param in request.files:
                    if 'image_file' in param and request.files.get(param):
                        index = int(param.rsplit('_',1)[1])
                        if len(image_links) < index + 1:
                            for i in range(index+1-len(image_links)):
                                image_links.append('')
                        image_path = save_upload_file(request.files.get(param))
                        if image_path:
                            clip_image((app.config['APPLICATION_DIR'] + image_path), size = content_image_size)
                        image_links[index] = image_path
            content.image_links = image_links
            content.save
            flash('Content "{name}" created successfully.'.format(name = content.name), 'success')
            return redirect(url_for('content.index', category_id = category_id))
    else:
        category = ContentCategory.query.get_or_404(category_id)
        options = category.options
        form = ContentForm()
    return render_template('content/new.html', form = form, options = options, category = category)

@content.route('/<int:id>')
def show(id):
    content = Content.query.get_or_404(id)
    return render_template('content/show.html', content = content)

@content.route('/<int:id>/edit', methods = ['GET', 'POST'])
def edit(id):
    content = Content.query.get_or_404(id)
    options = content.category.options
    if request.method == 'POST':
        form = ContentForm(request.form)
        if form.validate():
            option_ids = request.form.getlist('option_ids[]')
            request_options = ContentClassificationOption.query.filter(ContentClassificationOption.id.in_(option_ids))
            content = form.save(content)
            content.update_options(request_options)
            image_links = list(content.image_links)
            if request.files:
                for param in request.files:
                    if 'image_file' in param and request.files.get(param):
                        index = int(param.rsplit('_',1)[1])
                        if len(image_links) < index + 1:
                            for i in range(index+1-len(image_links)):
                                image_links.append('')
                        image_path = save_upload_file(request.files.get(param))
                        if image_path:
                            clip_image((app.config['APPLICATION_DIR'] + image_path), size = content_image_size)
                            delete_file(image_links[index])
                        image_links[index] = image_path
            content.image_links = image_links
            content.save
            flash('Content "{name}" has been updated.'.format(name = content.name), 'success')
            return redirect(url_for('content.index', category_id = content.category_id))
    else:
        form = ContentForm(obj = content)
    return render_template('content/edit.html', form = form, content = content, options = options)

@content.route('/<int:id>/delete', methods = ['GET', 'POST'])
def delete(id):
    content = Content.query.get_or_404(id)
    if request.method == 'POST':
        content.delete
        flash('Content "{name}" has been deleted.'.format(name = content.name), 'success')
        return redirect(url_for('content.title_index'))
    abort(404)

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
            category.save
            flash('Content category "{name}" created successfully.'.format(name = category.name), 'success')
            return redirect(url_for('content.category_index'))
    else:
        form = ContentCategoryForm()
    return render_template('content/category/new.html', form = form)

@content.route('/category/<int:id>')
def category_show(id):
    category = ContentCategory.query.get_or_404(id)
    return render_template('content/category/show.html', category = category)

@content.route('/category/<int:id>/edit', methods = ['GET', 'POST'])
def category_edit(id):
    category = ContentCategory.query.get_or_404(id)
    if request.method == 'POST':
        form = ContentCategoryForm(request.form)
        if form.validate():
            category = form.save(category)
            category.save
            flash('Content category "{name}" has been updated.'.format(name = category.name), 'success')
            return redirect(url_for('content.category_index'))
    else:
        form = ContentCategoryForm(obj = category)
    return render_template('content/category/edit.html', form = form, category = category)

@content.route('/category/<int:id>/delete', methods = ['GET', 'POST'])
def category_delete(id):
    category = ContentCategory.query.get_or_404(id)
    if request.method == 'POST':
        category.delete_p
        flash('Content category "{name}" has been deleted.'.format(name = category.name), 'success')
        return redirect(url_for('content.category_index'))
    return render_template('content/category/delete.html', category = category)

# url -- /content/classification/..
@content.route('/classification/new/<int:category_id>', methods = ['GET', 'POST'])
def classification_new(category_id):
    if request.method == 'POST':
        form = ContentClassificationForm(request.form)
        if form.validate():
            classification = form.save(ContentClassification(category_id = category_id))
            classification.save
            flash('Content classification "{name}" created successfully.'.format(name = classification.name), 'success')
            return redirect(url_for('content.category_show', id = category_id))
    else:
        form = ContentClassificationForm()
    return render_template('content/classification/new.html', form = form, category_id = category_id)

@content.route('/classification/<int:id>')
def classification_show(id):
    classification = ContentClassification.query.get_or_404(id)
    return render_template('content/classification/show.html', classification = classification)

@content.route('/classification/<int:id>/edit', methods = ['GET', 'POST'])
def classification_edit(id):
    classification = ContentClassification.query.get_or_404(id)
    if request.method == 'POST':
        form = ContentClassificationForm(request.form)
        if form.validate():
            classification = form.save(classification)
            classification.save
            flash('Content Classification "{name}" has been updated.'.format(name = classification.name), 'success')
            return redirect(url_for('content.category_show', id = classification.category_id))
    else:
        form = ContentClassificationForm(obj = classification)
    return render_template('content/classification/edit.html', form = form, classification = classification)

@content.route('/classification/<int:id>/delete', methods = ['GET', 'POST'])
def classification_delete(id):
    classification = ContentClassification.query.get_or_404(id)
    if request.method == 'POST':
        classification.delete_p
        flash('Content classification "{name}" has been deleted.'.format(name = classification.name), 'success')
        return redirect(url_for('content.category_show', id = classification.category_id))
    return render_template('content/classification/delete.html', classification = classification)

# url -- /content/option/..
@content.route('/option/new/<int:classification_id>', methods = ['GET', 'POST'])
def option_new(classification_id):
    if request.method == 'POST':
        form = ContentClassificationOptionForm(request.form)
        if form.validate():
            option = form.save(ContentClassificationOption(classification_id = classification_id))
            option.save
            flash('Content classification Option "{name}" created successfully.'.format(name = option.name), 'success')
            return redirect(url_for('content.classification_show', id = classification_id))
    else:
        form = ContentClassificationOptionForm()
    return render_template('content/option/new.html', form = form, classification_id = classification_id)

@content.route('/option/<int:id>')
def option_show(id):
    option = ContentClassificationOption.query.get_or_404(id)
    return render_template('content/option/show.html', option = option)

@content.route('/option/<int:id>/edit', methods = ['GET', 'POST'])
def option_edit(id):
    option = ContentClassificationOption.query.get_or_404(id)
    if request.method == 'POST':
        form = ContentClassificationOptionForm(request.form)
        if form.validate():
            option = form.save(option)
            option.save
            flash('Content Classification Option "{name}" has been updated.'.format(name = option.name), 'success')
            return redirect(url_for('content.classification_show', id = option.classification_id))
    else:
        form = ContentClassificationOptionForm(obj = option)
    return render_template('content/option/edit.html', form = form, option = option)

@content.route('/option/<int:id>/delete', methods = ['GET', 'POST'])
def option_delete(id):
    option = ContentClassificationOption.query.get_or_404(id)
    if request.method == 'POST':
        option.delete
        flash('Content classification option "{name}" has been deleted.'.format(name = option.name), 'success')
        return redirect(url_for('content.classification_show', id = option.classification_id))
    return render_template('content/option/delete.html', option = option)

# --- Material need ---
@content.route('/material_application/index')
def material_application_index():
    applications = MaterialApplication.query.all()
    return render_template('content/material_application/index.html', applications = applications)

@content.route('/material_application/<int:id>')
def material_application_show(id):
    application = MaterialApplication.query.get_or_404(id)
    return render_template('content/material_application/show.html', application = application)

@content.route('/material_application/<int:id>/approve')
def material_application_approve(id):
    application = MaterialApplication.query.get_or_404(id)
    application.status = '通过申请'
    application.save
    return redirect(url_for('content.material_application_index'))

@content.route('/material_application/<int:id>/reject')
def material_application_reject(id):
    application = MaterialApplication.query.get_or_404(id)
    application.status = '拒绝申请'
    application.save
    return redirect(url_for('content.material_application_index'))

@content.route('/material/index')
def material_index():
    materials = Material.query.all()
    return render_template('content/material_application/material_index.html', materials = materials)

@content.route('/material/new', methods = ['GET', 'POST'])
def material_new():
    if request.method == 'POST':
        form = MaterialForm(request.form)
        if form.validate():
            material = form.save(Material())
            material.save
            flash('material created successfully', 'success')
        else:
            flash('material created failure', 'danger')
        return redirect(url_for('content.material_index'))
    form = MaterialForm()
    return render_template('content/material_application/material_new.html', form = form)

@content.route('/material/<int:id>/edit', methods = ['GET', 'POST'])
def material_edit(id):
    material = Material.query.get_or_404(id)
    if request.method == 'POST':
        form = MaterialForm(request.form)
        if form.validate():
            material = form.save(material)
            material.save
            flash('material has been updated successfully', 'success')
        else:
            flash('material updated failure', 'danger')
        return redirect(url_for('content.material_index'))
    else:
        form = MaterialForm(obj = material)
    return render_template('content/material_application/material_edit.html', material = material, form = form)
