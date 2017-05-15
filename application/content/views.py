# -*- coding: utf-8 -*-
import os, datetime
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from .. import app, db, cache
from ..helpers import object_list, save_upload_file, delete_file, clip_image
from ..models import Content, ContentCategory, ContentClassification, ContentClassificationOption
from ..models import Material, MaterialApplication, MaterialApplicationContent, LogisticsCompanyInfo
from ..wechat.models import WechatCall
from .forms import *

content = Blueprint('content', __name__, template_folder='templates')
content_image_size = (379, 226)


# url -- /content/..
@content.route('/')
def root():
    return redirect(url_for('content.index'))


@content.route('/index/<int:category_id>/')
def index(category_id):
    category = ContentCategory.query.get_or_404(category_id)
    query = Content.query.filter(Content.category_id == category_id)
    if request.args.get('name'):
        query = query.filter(Content.name.contains(request.args.get('name')))
    contents = query.order_by(Content.created_at.desc())
    return object_list('content/index.html', contents, paginate_by=20, category=category)


@content.route('/new/<int:category_id>', methods=['GET', 'POST'])
def new(category_id):
    if request.method == 'POST':
        form = ContentForm(request.form)
        if form.validate():
            option_ids = request.form.getlist('option_ids[]') 
            request_options = ContentClassificationOption.query.filter(ContentClassificationOption.id.in_(option_ids))
            content = form.save(Content(category_id=category_id))
            content.append_options(request_options)
            image_links = []
            if request.files:
                for param in request.files:
                    if 'image_file' in param and request.files.get(param):
                        index = int(param.rsplit('_', 1)[1])
                        if len(image_links) < index + 1:
                            for i in range(index+1-len(image_links)):
                                image_links.append('')
                        image_path = save_upload_file(request.files.get(param))
                        if image_path:
                            clip_image((app.config['APPLICATION_DIR'] + image_path), size=content_image_size)
                        image_links[index] = image_path
            content.image_links = image_links
            content.save
            flash('Content "{name}" created successfully.'.format(name=content.name), 'success')
            return redirect(url_for('content.index', category_id=category_id))
    else:
        category = ContentCategory.query.get_or_404(category_id)
        options = category.options
        form = ContentForm()
    return render_template('content/new.html', form=form, options=options, category=category)


@content.route('/<int:id>')
def show(id):
    content = Content.query.get_or_404(id)
    return render_template('content/show.html', content=content)


@content.route('/<int:id>/edit', methods=['GET', 'POST'])
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
                        index = int(param.rsplit('_', 1)[1])
                        if len(image_links) < index + 1:
                            for i in range(index+1-len(image_links)):
                                image_links.append('')
                        image_path = save_upload_file(request.files.get(param))
                        if image_path:
                            clip_image((app.config['APPLICATION_DIR'] + image_path), size=content_image_size)
                            delete_file(image_links[index])
                        image_links[index] = image_path
            content.image_links = image_links
            content.save
            flash('Content "{name}" has been updated.'.format(name=content.name), 'success')
            return redirect(url_for('content.index', category_id=content.category_id))
    else:
        form = ContentForm(obj = content)
    return render_template('content/edit.html', form=form, content=content, options=options)


@content.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    content = Content.query.get_or_404(id)
    if request.method == 'POST':
        content.delete
        flash('Content "{name}" has been deleted.'.format(name=content.name), 'success')
        if request.args.get('back_url'):
            return redirect(request.args.get('back_url'))
        return redirect(url_for('content.category_index'))


# url -- /content/category/..
@content.route('/category/index')
def category_index():
    categories = ContentCategory.query.order_by(ContentCategory.created_at.asc())
    return render_template('content/category/index.html', categories=categories)


@content.route('/category/new', methods=['GET', 'POST'])
def category_new():
    if request.method == 'POST':
        form = ContentCategoryForm(request.form)
        if form.validate():
            category = form.save(ContentCategory())
            category.save
            flash('Content category "{name}" created successfully.'.format(name=category.name), 'success')
            return redirect(url_for('content.category_index'))
    else:
        form = ContentCategoryForm()
    return render_template('content/category/new.html', form = form)


@content.route('/category/<int:id>')
def category_show(id):
    category = ContentCategory.query.get_or_404(id)
    return render_template('content/category/show.html', category=category)


@content.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def category_edit(id):
    category = ContentCategory.query.get_or_404(id)
    if request.method == 'POST':
        form = ContentCategoryForm(request.form)
        if form.validate():
            category = form.save(category)
            category.save
            flash('Content category "{name}" has been updated.'.format(name=category.name), 'success')
            return redirect(url_for('content.category_index'))
    else:
        form = ContentCategoryForm(obj=category)
    return render_template('content/category/edit.html', form=form, category=category)


@content.route('/category/<int:id>/delete', methods=['GET', 'POST'])
def category_delete(id):
    category = ContentCategory.query.get_or_404(id)
    if request.method == 'POST':
        category.delete_p
        flash('Content category "{name}" has been deleted.'.format(name=category.name), 'success')
        return redirect(url_for('content.category_index'))
    return render_template('content/category/delete.html', category=category)


# url -- /content/classification/..
@content.route('/classification/new/<int:category_id>', methods=['GET', 'POST'])
def classification_new(category_id):
    if request.method == 'POST':
        form = ContentClassificationForm(request.form)
        if form.validate():
            classification = form.save(ContentClassification(category_id=category_id))
            classification.save
            flash('Content classification "{name}" created successfully.'.format(name=classification.name), 'success')
            return redirect(url_for('content.category_show', id=category_id))
    else:
        form = ContentClassificationForm()
    return render_template('content/classification/new.html', form=form, category_id=category_id)


@content.route('/classification/<int:id>')
def classification_show(id):
    classification = ContentClassification.query.get_or_404(id)
    return render_template('content/classification/show.html', classification=classification)


@content.route('/classification/<int:id>/edit', methods=['GET', 'POST'])
def classification_edit(id):
    classification = ContentClassification.query.get_or_404(id)
    if request.method == 'POST':
        form = ContentClassificationForm(request.form)
        if form.validate():
            classification = form.save(classification)
            classification.save
            flash('Content Classification "{name}" has been updated.'.format(name=classification.name), 'success')
            return redirect(url_for('content.category_show', id=classification.category_id))
    else:
        form = ContentClassificationForm(obj=classification)
    return render_template('content/classification/edit.html', form=form, classification=classification)


@content.route('/classification/<int:id>/delete', methods=['GET', 'POST'])
def classification_delete(id):
    classification = ContentClassification.query.get_or_404(id)
    if request.method == 'POST':
        classification.delete_p
        flash('Content classification "{name}" has been deleted.'.format(name=classification.name), 'success')
        return redirect(url_for('content.category_show', id=classification.category_id))
    return render_template('content/classification/delete.html', classification=classification)


# url -- /content/option/..
@content.route('/option/new/<int:classification_id>', methods=['GET', 'POST'])
def option_new(classification_id):
    if request.method == 'POST':
        form = ContentClassificationOptionForm(request.form)
        if form.validate():
            option = form.save(ContentClassificationOption(classification_id=classification_id))
            option.save
            flash('Content classification Option "{name}" created successfully.'.format(name=option.name), 'success')
            return redirect(url_for('content.classification_show', id=classification_id))
    else:
        form = ContentClassificationOptionForm()
    return render_template('content/option/new.html', form = form, classification_id = classification_id)


@content.route('/option/<int:id>')
def option_show(id):
    option = ContentClassificationOption.query.get_or_404(id)
    return render_template('content/option/show.html', option=option)


@content.route('/option/<int:id>/edit', methods=['GET', 'POST'])
def option_edit(id):
    option = ContentClassificationOption.query.get_or_404(id)
    if request.method == 'POST':
        form = ContentClassificationOptionForm(request.form)
        if form.validate():
            option = form.save(option)
            option.save
            flash('Content Classification Option "{name}" has been updated.'.format(name=option.name), 'success')
            return redirect(url_for('content.classification_show', id=option.classification_id))
    else:
        form = ContentClassificationOptionForm(obj=option)
    return render_template('content/option/edit.html', form=form, option=option)


@content.route('/option/<int:id>/delete', methods=['GET', 'POST'])
def option_delete(id):
    option = ContentClassificationOption.query.get_or_404(id)
    if request.method == 'POST':
        option.delete
        flash('Content classification option "{name}" has been deleted.'.format(name=option.name), 'success')
        return redirect(url_for('content.classification_show', id=option.classification_id))
    return render_template('content/option/delete.html', option=option)


# --- Material need ---
# 所有物料申请审批都转到市场部
@content.route('/material_application/index/')
def material_application_index():
    form = MaterialApplicationSearchForm(request.args)
    query = MaterialApplication.query.filter(
        MaterialApplication.user_id.in_(
            set([user.id for user in current_user.get_subordinate_dealers()] +
                [user.id for user in User.query.filter(User.user_or_origin == 3)])))
    if form.created_at_gt.data:
        query = query.filter(MaterialApplication.created_at >= form.created_at_gt.data)
    if form.created_at_lt.data:
        query = query.filter(MaterialApplication.created_at <= form.created_at_lt.data)
    if form.app_no.data:
        query = query.filter(MaterialApplication.app_no.contains(form.app_no.data))
    if request.args.get('sales_area'):
        query = query.filter(MaterialApplication.sales_area == request.args.get('sales_area'))
    if request.args.get('status'):
        query = query.filter(MaterialApplication.status == request.args.get('status'))
    if request.args.get('app_type'):
        query = query.filter(MaterialApplication.app_type == request.args.get('app_type'))
    applications = query.order_by(MaterialApplication.created_at.desc())
    return object_list('content/material_application/index.html', applications, paginate_by=20, form=form)


# 物料申请后台创建入口, 员工用
@content.route('/material_application/new', methods=['GET', 'POST'])
def material_application_new():
    if not current_user.is_staff():
        flash('只有员工帐号才能使用此功能', 'danger')
        return redirect(url_for('content.material_application_index'))

    if request.method == 'POST':
        app_contents = []
        app_infos = {
            'customer': request.form.get('customer'),
            'project_name': request.form.get('project_name'),
            'purpose': request.form.get('purpose'),
            'delivery_method': request.form.get('delivery_method'),
            'receive_address': request.form.get('receive_address'),
            'receiver': request.form.get('receiver'),
            'receiver_tel': request.form.get('receiver_tel')
        }
        if request.form:
            for param in request.form:
                if 'material' in param and request.form.get(param):
                    if int(request.form.get(param)) > 0:
                        app_contents.append([param.split('_', 1)[1], request.form.get(param)])

        if app_contents:
            application = MaterialApplication(app_no='MA' + datetime.datetime.now().strftime('%y%m%d%H%M%S'),
                                              user=current_user, status='新申请', app_memo=request.form.get('app_memo'),
                                              app_type=3, sales_area=request.form.get('sales_area'), app_infos=app_infos
                                              )
            db.session.add(application)
            for app_content in app_contents:
                material = Material.query.get_or_404(app_content[0])
                ma_content = MaterialApplicationContent(material_id=material.id, material_name=material.name,
                                                        number=app_content[1], application=application)
                db.session.add(ma_content)
            db.session.commit()
            flash('物料申请提交成功', 'success')
        else:
            flash('请输入正确的数量', 'danger')
        return redirect(url_for('content.material_application_index'))
    else:
        materials = Material.query.order_by(Material.name.desc())
        form = MaterialApplicationForm2()
        today = datetime.datetime.now().strftime('%F')
        departments = ', '.join([department.name for department in current_user.departments])
    return render_template('content/material_application/new.html', form=form, materials=materials, today=today,
                           departments=departments)


@content.route('/material_application/<int:id>')
def material_application_show(id):
    application = MaterialApplication.query.get_or_404(id)
    return render_template('content/material_application/show.html', application=application)


@content.route('/material_application/<int:id>/edit', methods=['GET', 'POST'])
def material_application_edit(id):
    application = MaterialApplication.query.get_or_404(id)
    if request.method == 'POST':
        form = MaterialApplicationForm(request.form)
        if form.validate():
            application = form.save(application)
            db.session.add(application)
            for param in request.form:
                if 'content' in param and request.form.get(param):
                    content = MaterialApplicationContent.query.get(param.rsplit('_', 1)[1])
                    content.available_number = request.form.get(param)
                    db.session.add(content)
            db.session.commit()
            flash('审核成功', 'success')
            cache.delete_memoized(current_user.get_material_application_num)
        else:
            flash('审核失败', 'danger')
        if application.user.is_dealer():
            WechatCall.send_template_to_user(str(application.user_id),
                                             "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0",
                                             {
                                                 "first": {
                                                     "value": "您的物料申请订单状态已更改",
                                                     "color": "#173177"
                                                 },
                                                 "keyword1": {
                                                     "value": application.app_no,
                                                     "color": "#173177"
                                                 },
                                                 "keyword2": {
                                                     "value": application.status,
                                                     "color": "#173177"
                                                 },
                                                 "keyword3": {
                                                     "value": application.memo,
                                                     "color": "#173177"
                                                 },
                                                 "remark": {
                                                     "value": "感谢您的使用！",
                                                     "color": "#173177"
                                                 },
                                             },
                                             url_for('mobile_material_application_show', id=application.id)
                                             )
        return redirect(url_for('content.material_application_index'))
    form = MaterialApplicationForm(obj=application)
    return render_template('content/material_application/edit.html', application=application, form=form)


@content.route('/material/index')
def material_index():
    materials = Material.query.order_by(Material.created_at.asc())
    return render_template('content/material_application/material_index.html', materials=materials)


@content.route('/material/statistics')
def material_statistics():
    materials = Material.query.order_by(Material.created_at.desc())
    material_names = [material.name for material in materials]
    material_stock_nums = [material.stock_num for material in materials]
    material_used_nums = [material.used_num for material in materials]
    material_remain_nums = [material.remain_num for material in materials]
    return render_template('content/material_application/material_statistics.html', material_names=material_names,
                           material_stock_nums=material_stock_nums, material_used_nums=material_used_nums,
                           material_remain_nums=material_remain_nums)


@content.route('/material/new', methods=['GET', 'POST'])
def material_new():
    if request.method == 'POST':
        form = MaterialForm(request.form)
        if form.validate():
            material = form.save(Material())
            db.session.add(material)
            db.session.commit()
            flash('material created successfully', 'success')
        else:
            flash('material created failure', 'danger')
        return redirect(url_for('content.material_index'))
    form = MaterialForm()
    return render_template('content/material_application/material_new.html', form=form)


@content.route('/material/<int:id>/edit', methods=['GET', 'POST'])
def material_edit(id):
    material = Material.query.get_or_404(id)
    if request.method == 'POST':
        form = MaterialForm(request.form)
        if form.validate():
            material = form.save(material)
            db.session.add(material)
            db.session.commit()
            flash('material has been updated successfully', 'success')
        else:
            flash('material updated failure', 'danger')
        return redirect(url_for('content.material_index'))
    else:
        form = MaterialForm(obj=material)
    return render_template('content/material_application/material_edit.html', material=material, form=form)


@content.route('/material/<int:id>/delete')
def material_delete(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash('%s has been deleted successfully' % material.name, 'success')
    return redirect(url_for('content.material_index'))


@content.route('/logistics_company_info/index')
def logistics_company_info_index():
    logistics_company_infos = LogisticsCompanyInfo.query.order_by(LogisticsCompanyInfo.created_at.desc())
    return render_template('content/logistics_company_info/index.html', logistics_company_infos=logistics_company_infos)


@content.route('/logistics_company_info/new', methods=['GET', 'POST'])
def logistics_company_info_new():
    if request.method == 'POST':
        form = LogisticsCompanyInfoForm(request.form)
        if form.validate():
            logistics_company_info = form.save(LogisticsCompanyInfo())
            db.session.add(logistics_company_info)
            db.session.commit()
            flash('货运公司"%s"创建成功' % logistics_company_info.name, 'success')
            return redirect(url_for('content.logistics_company_info_index'))
    else:
        form = LogisticsCompanyInfoForm()
    return render_template('content/logistics_company_info/new.html', form=form)


@content.route('/logistics_company_info/<int:id>/edit', methods=['GET', 'POST'])
def logistics_company_info_edit(id):
    logistics_company_info = LogisticsCompanyInfo.query.get_or_404(id)
    if request.method == 'POST':
        form = LogisticsCompanyInfoForm(request.form)
        if form.validate():
            logistics_company_info = form.save(logistics_company_info)
            db.session.add(logistics_company_info)
            db.session.commit()
            flash('货运公司修改成功', 'success')
            return redirect(url_for('content.logistics_company_info_index'))
    else:
        form = LogisticsCompanyInfoForm(obj=logistics_company_info)
    return render_template('content/logistics_company_info/edit.html', logistics_company_info=logistics_company_info,
                           form=form)


@content.route('/logistics_company_info/<int:id>/delete')
def logistics_company_info_delete(id):
    logistics_company_info = LogisticsCompanyInfo.query.get_or_404(id)
    db.session.delete(logistics_company_info)
    db.session.commit()
    flash('"%s"删除成功' % logistics_company_info.name, 'success')
    return redirect(url_for('content.logistics_company_info_index'))
