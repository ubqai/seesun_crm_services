# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, request, url_for
from .. import db
from ..helpers import save_upload_file, delete_file, clip_image
from .api import *
from ..models import Content, ContentCategory

product = Blueprint('product', __name__, template_folder='templates')

product_image_size = (379, 226)
sku_image_size = (290, 290)


@product.route('/index/<int:category_id>')
def index(category_id):
    products = load_products(category_id, only_valid=False)
    category = load_category(category_id)
    return render_template('product/index.html', products=products, category=category)


@product.route('/new/<int:category_id>', methods=['GET', 'POST'])
def new(category_id):
    if request.method == 'POST':
        option_ids = request.form.getlist('option_ids[]')
        image_files = [request.files.get('image_file_0'), request.files.get('image_file_1')]
        product_image_links = []
        for image_file in image_files:
            if image_file:
                image_path = save_upload_file(image_file)
                if image_path:
                    clip_image((app.config['APPLICATION_DIR'] + image_path), size=product_image_size)
            else:
                image_path = ''
            product_image_links.append(image_path)
        product_info = {
            'name': request.form.get('name'),
            'code': request.form.get('code'),
            'length': request.form.get('length'),
            'width': request.form.get('width'),
            'description': request.form.get('description'),
            'product_image_links': product_image_links,
            'case_ids': [],
            'options_id': [str(option_id) for option_id in option_ids]
        }
        data = {
            'product_category_id': str(category_id),
            'product_info': product_info
        }
        response = create_product(data)
        if response.status_code == 201:
            return redirect(url_for('product.sku_index', product_id=int(response.json().get('product_id'))))
        return redirect(url_for('product.index', category_id=category_id))
    category = load_category(category_id)
    features = load_features()
    return render_template('product/new.html', category=category, features=features)


@product.route('/relate_cases/<int:product_id>', methods=['GET', 'POST'])
def relate_cases(product_id):
    _product = load_product(product_id)
    contents = ContentCategory.query.filter(ContentCategory.name == '案例展示').first().contents
    if request.method == 'POST':
        case_ids = [int(case_id) for case_id in request.form.getlist('case_ids[]')]
        data = {'case_ids': case_ids}
        response = update_product(_product.get('product_id'), data=data)
        if response.status_code == 200:
            for content in contents:
                if content.id in case_ids:
                    if product_id not in content.product_ids:
                        temp = list(content.product_ids)
                        temp.append(product_id)
                        content.product_ids = temp
                        db.session.add(content)
                else:
                    if product_id in content.product_ids:
                        temp = list(content.product_ids)
                        temp.remove(product_id)
                        content.product_ids = temp
                        db.session.add(content)
            db.session.commit()
            flash('关联案例修改成功', 'success')
        else:
            flash('关联案例修改失败', 'danger')
        return redirect(url_for('product.category_index'))
    return render_template('product/relate_cases.html', product=_product, contents=contents)


@product.route('/<int:id>')
def show(id):
    category = load_category(request.args.get('category_id'))
    _product = load_product(id, option_sorted=True)
    skus = load_skus(id)
    contents = Content.query.filter(Content.id.in_(_product.get('case_ids')))
    option_sorted = _product.get('option_sorted')
    return render_template('product/show.html', category=category, product=_product, skus=skus, contents=contents,
                           option_sorted=option_sorted)


@product.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    category_id = request.args.get('category_id')
    if not category_id:
        return redirect(url_for('product.category_index'))
    _product = load_product(id)
    category = load_category(category_id)
    features = load_features()
    option_ids = [x.get('option_id') for x in load_product_options(_product.get('product_id')).get('options')]
    if request.method == 'POST':
        option_ids = request.form.getlist('option_ids[]')
        product_image_links = _product.get('images') or []
        if request.files:
            for param in request.files:
                if 'image_file' in param and request.files.get(param):
                    _index = int(param.rsplit('_', 1)[1])
                    if len(product_image_links) < _index + 1:
                        for i in range(_index+1-len(product_image_links)):
                            product_image_links.append('')
                    image_path = save_upload_file(request.files.get(param))
                    if image_path:
                        clip_image((app.config['APPLICATION_DIR'] + image_path), size=product_image_size)
                        if product_image_links[_index]:
                            delete_file(product_image_links[_index])
                        product_image_links[_index] = image_path
        data = {
            'name': request.form.get('name'),
            'length': request.form.get('length'),
            'width': request.form.get('width'),
            'description': request.form.get('description'),
            'product_image_links': product_image_links,
            'options_id': [str(option_id) for option_id in option_ids],
            'isvalid': request.form.get('isvalid')
        }
        response = update_product(id, data=data)
        if response.status_code == 200:
            flash('产品修改成功', 'success')
        else:
            flash('产品修改失败: %s' % response.json(), 'danger')
        return redirect(url_for('product.index', category_id=category_id))
    return render_template('product/edit.html', product=_product, category=category, features=features,
                           option_ids=option_ids)


@product.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if request.method == 'POST':
        category_id = request.args.get('category_id')
        response = delete_product(id)
        if response.status_code == 200:
            flash('产品删除成功', 'success')
        else:
            flash('产品删除失败', 'danger')
        if category_id:
            return redirect(url_for('product.index', category_id=category_id))
        return redirect(url_for('product.category_index'))


@product.route('/sku/index/<int:product_id>')
def sku_index(product_id):
    skus = load_skus(product_id)
    # _product = load_product(product_id)
    features = load_features()
    option_ids = [x.get('option_id') for x in load_product_options(product_id).get('options')]
    return render_template('product/sku/index.html', skus=skus, product_id=product_id,
                           features=features, option_ids=option_ids)


@product.route('/sku/new/<int:product_id>', methods=['GET', 'POST'])
def sku_new(product_id):
    if request.method == 'POST':
        option_ids = request.form.getlist('option_ids[]')
        image_file = request.files.get('image_file')
        if image_file:
            image_path = save_upload_file(image_file)
            if image_path:
                clip_image((app.config['APPLICATION_DIR'] + image_path), size=sku_image_size)
        else:
            image_path = ''
        sku_infos = []
        sku_info = {
            'code': request.form.get('code'),
            'barcode': request.form.get('barcode') or None,
            'hscode': request.form.get('hscode') or None,
            'weight': request.form.get('weight') or None,
            'thumbnail': image_path,
            'name': request.form.get('name') or None,
            'memo': request.form.get('memo') or None,
            'options_id': [str(option_id) for option_id in option_ids]
        }
        sku_infos.append(sku_info)
        data = {
            'product_id': str(product_id),
            'sku_infos': sku_infos
        }
        response = create_sku(data)
        if response.status_code == 201:
            flash('SKU创建成功', 'success')
        else:
            flash('SKU创建失败', 'danger')
        return redirect(url_for('product.sku_index', product_id=product_id))
    _product = load_product(product_id, option_sorted=True)
    option_sorted = _product.get('option_sorted')
    return render_template('product/sku/new.html', product=_product, option_sorted=option_sorted)


@product.route('/sku/<int:id>/edit', methods=['GET', 'POST'])
def sku_edit(id):
    product_id = request.args.get('product_id')
    if not product_id:
        return redirect(url_for('product.category_index'))
    sku = load_sku(product_id=product_id, sku_id=id)
    if request.method == 'POST':
        option_ids = []
        for option_id in request.form.getlist('option_ids[]'):
            if option_id:
                option_ids.append(option_id)
        image_file = request.files.get('image_file')
        if image_file:
            image_path = save_upload_file(image_file)
            if image_path:
                clip_image((app.config['APPLICATION_DIR'] + image_path), size=sku_image_size)
                if sku.get('thumbnail'):
                    delete_file(sku.get('thumbnail'))
        else: 
            image_path = sku.get('thumbnail')
        data = {
            'barcode': request.form.get('barcode'),
            'hscode': request.form.get('hscode'),
            'weight': request.form.get('weight') or None,
            'isvalid': request.form.get('isvalid'),
            'thumbnail': image_path,
            'name': request.form.get('name'),
            'memo': request.form.get('memo'),
            'options_id': [str(option_id) for option_id in option_ids] or None
        }
        if not request.form.get('code') == sku.get('code'):
            data['code'] = request.form.get('code')
        response = update_sku(sku_id=id, data=data)
        if response.status_code == 200:
            flash('SKU修改成功', 'success')
        else:
            flash('SKU修改失败', 'danger')
        return redirect(url_for('product.sku_index', product_id=product_id))
    _product = load_product(product_id, option_sorted=True)
    option_sorted = _product.get('option_sorted')
    option_set = []
    for option in sku.get('options'):
        for key in option:
            option_set.append([key, option[key]])
    return render_template('product/sku/edit.html', sku=sku, product=_product, option_set=option_set,
                           option_sorted=option_sorted)


@product.route('/sku/<int:id>/delete', methods=['POST'])
def sku_delete(id):
    product_id = request.args.get('product_id')
    if request.method == 'POST':
        response = delete_sku(id)
        if response.status_code == 200:
            flash('SKU删除成功', 'success')
        else:
            flash('SKU删除失败', 'danger')
        if product_id:
            return redirect(url_for('product.sku_index', product_id=product_id))
        return redirect(url_for('product.category_index'))

"""
@product.route('/sku/batch_new/<int:product_id>', methods = ['GET', 'POST'])
def sku_batch_new(product_id):
    if request.method == 'POST':
        if request.form.get('sku_count'):
            sku_infos = []
            for i in range(int(request.form.get('sku_count'))):
                if request.form.get('%s_code' % i) and request.form.get('%s_barcode' % i):
                    option_ids = request.form.getlist('%s_option_ids[]' % i)
                    image_file = request.files.get('image_file')
                    if image_file:
                        image_path = save_upload_file(image_file)
                    else:
                        image_path = '' 
                    sku_info = {
                    'code': str(request.form.get('%s_code' % i)),
                    'price': str(request.form.get('%s_price' % i)),
                    'stocks': str(request.form.get('%s_stocks' % i)),
                    'barcode': str(request.form.get('%s_barcode' % i)),
                    'hscode': str(request.form.get('%s_hscode' % i)),
                    'weight': str(request.form.get('%s_weight' % i)),
                    'thumbnail': image_path,
                    'options_id': [str(id) for id in option_ids]
                    }
                    sku_infos.append(sku_info)
            data = {
            'product_id': str(product_id),
            'sku_infos': sku_infos
            }
            response = create_sku(data)
        return redirect(url_for('product.sku_index', product_id = product_id))
    product = load_product(product_id)
    options = product.get('options')
    # first, find out all feature name
    feature_list = []
    for option in options:
        if not option.get('feature_name') in feature_list:
            feature_list.append(option.get('feature_name'))
    # second, sort options by feature list
    option_sorted_by_feature = []
    for feature in feature_list:
        group = []
        for option in options:
            if option.get('feature_name') == feature:
                group.append(option)
        option_sorted_by_feature.append(group)
    # third, combine options with different feature name
    num_arr = [len(i) for i in option_sorted_by_feature]
    x = []
    for i in range(int(''.join(map(str, num_arr)))):
        v = True
        for j in zip(list(str(i).zfill(len(option_sorted_by_feature))), num_arr):
            if int(j[0]) >= j[1]:
                v = False
        if v == True:
            x.append(list(map(int, list(str(i).zfill(len(num_arr))))))
    option_combinations = []
    for i in x:
        temp = []
        for j,k in enumerate(i):
            temp.append(option_sorted_by_feature[j][k])
        option_combinations.append(temp)

    return render_template('product/sku/batch_new.html', product = product, option_combinations = option_combinations)
"""


@product.route('/category/index')
def category_index():
    categories = load_categories()
    return render_template('product/category/index.html', categories=categories)


@product.route('/category/new', methods=['GET', 'POST'])
def category_new():
    if request.method == 'POST':
        category_names = request.form.getlist('names[]')
        for name in category_names:
            if len(name) == 0:
                flash('Please input correct names', 'danger')
                return render_template('product/category/new.html')
        data = {'category_names': category_names}
        response = create_category(data)
        if response.status_code == 201:
            flash('产品目录创建成功', 'success')
        else:
            flash('产品目录创建失败', 'danger')
        return redirect(url_for('product.category_index'))
    return render_template('product/category/new.html')


@product.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def category_edit(id):
    category = load_category(id)
    if request.method == 'POST':
        name = request.form.get('name')
        data = {'category_name': name}
        response = update_category(category.get('category_id'), data=data)
        if response.status_code == 200:
            flash('产品目录修改成功', 'success')
        else:
            flash('产品目录修改失败', 'danger')
        return redirect(url_for('product.category_index'))
    return render_template('product/category/edit.html', category=category)


@product.route('/feature/index')
def feature_index():
    features = load_features()
    return render_template('product/feature/index.html', features=features)


@product.route('/feature/new', methods=['GET', 'POST'])
def feature_new():
    if request.method == 'POST':
        feature_names = request.form.getlist('names[]')
        for name in feature_names:
            if len(name) == 0:
                flash('Please input correct names', 'danger')
                return render_template('product/feature/new.html')
        feature_infos = []
        for name in feature_names:
            feature_infos.append({'name': name, 'description': name})
        data = {
            'feature_infos': feature_infos
        }
        response = create_feature(data)
        if response.status_code == 201:
            flash('产品属性创建成功', 'success')
        else:
            flash('产品属性创建失败', 'danger')
        return redirect(url_for('product.feature_index'))
    return render_template('product/feature/new.html')


@product.route('/feature/<int:id>')
def feature_show(id):
    feature = load_feature(id)
    return render_template('product/feature/show.html', feature=feature)


@product.route('/feature/<int:id>/edit', methods=['GET', 'POST'])
def feature_edit(id):
    feature = load_feature(id)
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        response = update_feature(feature.get('feature_id'), data=data)
        if response.status_code == 200:
            flash('产品属性修改成功', 'success')
        else:
            flash('产品属性修改失败', 'danger')
        return redirect(url_for('product.feature_index'))
    return render_template('product/feature/edit.html', feature=feature)


@product.route('/feature/<int:id>/delete')
def feature_delete(id):
    response = delete_feature(id)
    if response.status_code == 200:
        flash('产品属性删除成功', 'success')
    else:
        flash('产品属性删除失败', 'danger')
    return redirect(url_for('product.feature_index'))


@product.route('/option/new/<int:feature_id>', methods=['GET', 'POST'])
def option_new(feature_id):
    if request.method == 'POST':
        option_names = request.form.getlist('names[]')
        for name in option_names:
            if len(name) == 0:
                flash('Please input correct names', 'danger')
                return render_template('product/option/new.html', feature_id=feature_id)
        data = {
            'sku_feature_id': str(feature_id),
            'names': option_names
        }
        response = create_option(data)
        if response.status_code == 201:
            flash('产品属性值创建成功', 'success')
        else:
            flash('产品属性值创建失败', 'danger')
        return redirect(url_for('product.feature_index'))
    feature = load_feature(feature_id)
    return render_template('product/option/new.html', feature=feature)


@product.route('/option/<int:id>/edit', methods=['GET', 'POST'])
def option_edit(id):
    if request.method == 'POST':
        data = {'name': request.form.get('name')}
        response = update_option(id, data=data)
        if response.status_code == 200:
            flash('产品属性值修改成功', 'success')
        else:
            flash('产品属性值修改失败', 'danger')
        return redirect(url_for('product.feature_index'))
    feature = load_feature(request.args.get('feature_id'))
    return render_template('product/option/edit.html', option_id=id, feature=feature)


@product.route('/option/<int:id>/delete')
def option_delete(id):
    response = delete_option(id)
    if response.status_code == 200:
        flash('产品属性值删除成功', 'success')
    else:
        flash('产品属性值删除失败', 'danger')
    return redirect(url_for('product.feature_index'))
