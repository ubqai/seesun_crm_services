# -*- coding: utf-8 -*-
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from .. import app
from ..helpers import save_upload_file, clip_image
from .api import *

product = Blueprint('product', __name__, template_folder = 'templates')

product_image_size = (379, 226)

@product.route('/index/<int:category_id>')
def index(category_id):
    products = load_products(category_id)
    category = load_category(category_id)
    return render_template('product/index.html', products = products, category = category)

@product.route('/new/<int:category_id>', methods = ['GET', 'POST'])
def new(category_id):
    if request.method == 'POST':
        option_ids = request.form.getlist('option_ids[]')
        image_file = request.files.get('image_file')
        if image_file:
            image_path = save_upload_file(image_file)
            if image_path:
                clip_image((app.config['APPLICATION_DIR'] + image_path), size = product_image_size)
        else:
            image_path = ''
        url = '%s/api/products' % site
        product_info = {
        'name': request.form.get('name'),
        'code': request.form.get('code'),
        'description': request.form.get('description'),
        'product_image_links': [image_path],
        'options_id': [ str(id) for id in option_ids ]
        }
        data = {
        'product_category_id': str(category_id),
        'product_info': product_info
        }
        response = api_post(url, data)
        return redirect(url_for('product.index', category_id = category_id))
    category = load_category(category_id)
    features = load_features(category_id)
    return render_template('product/new.html', category = category, features = features)

@product.route('/<int:id>')
def show(id):
    product = load_product(id)
    return render_template('product/show.html', product = product)

@product.route('/sku/index/<int:product_id>')
def sku_index(product_id):
    skus = load_skus(product_id)
    return render_template('product/sku/index.html', skus = skus, product_id = product_id)

@product.route('/sku/new/<int:product_id>', methods = ['GET', 'POST'])
def sku_new(product_id):
    if request.method == 'POST':
        option_ids = request.form.getlist('option_ids[]')
        image_file = request.files.get('image_file')
        if image_file:
            image_path = save_upload_file(image_file)
        else:
            image_path = ''
        url = '%s/api/product_skus' % site
        sku_infos = []
        sku_info = {
        'code': str(request.form.get('code')),
        'price': str(request.form.get('price')),
        'stocks': str(request.form.get('stocks')),
        'barcode': str(request.form.get('barcode')),
        'hscode': str(request.form.get('hscode')),
        'weight': str(request.form.get('weight')),
        'thumbnail': image_path,
        'options_id': [str(id) for id in option_ids]
        }
        sku_infos.append(sku_info)
        data = {
        'product_id': str(product_id),
        'sku_infos': sku_infos
        }
        response = api_post(url, data)
        return redirect(url_for('product.sku_index', product_id = product_id))
    product = load_product(product_id)
    return render_template('product/sku/new.html', product = product)

@product.route('/category/index')
def category_index():
    categories = load_categories()
    return render_template('product/category/index.html', categories = categories)

@product.route('/category/new', methods = ['GET', 'POST'])
def category_new():
    if request.method == 'POST':
        category_names = request.form.getlist('names[]')
        for name in category_names:
            if len(name) == 0:
                flash('Please input correct names', 'danger')
                return render_template('product/category/new.html')
        url = site + '/api/product_categories'
        data = { 'category_names': category_names }
        response = api_post(url, data)
        return redirect(url_for('product.category_index'))
    return render_template('product/category/new.html')

@product.route('/category/<int:id>')
def category_show(id):
    category = load_category(id)
    return render_template('product/category/show.html', category = category)

@product.route('/feature/new/<int:category_id>', methods = ['GET', 'POST'])
def feature_new(category_id):
    if request.method == 'POST':
        feature_names = request.form.getlist('names[]')
        for name in feature_names:
            if len(name) == 0:
                flash('Please input correct names', 'danger')
                return render_template('product/feature/new.html', category_id = category_id)
        url = site + '/api/sku_features'
        feature_infos = []
        for name in feature_names:
            feature_infos.append({ 'name': name, 'description': name })
        data = {
        'product_category_id': str(category_id),
        'feature_infos': feature_infos
        }
        response = api_post(url, data)
        flash('Product sku feature created successfully', 'success')
        return redirect(url_for('product.category_show', id = category_id))
    return render_template('product/feature/new.html', category_id = category_id)

@product.route('/feature/<int:id>')
def feature_show(id):
    feature = load_feature(id)
    return render_template('product/feature/show.html', feature = feature)

@product.route('/option/new/<int:feature_id>', methods = ['GET', 'POST'])
def option_new(feature_id):
    if request.method == 'POST':
        option_names = request.form.getlist('names[]')
        for name in option_names:
            if len(name) == 0:
                flash('Please input correct names', 'danger')
                return render_template('product/option/new.html', feature_id = feature_id)
        url = site + '/api/sku_options'
        data = {
        'sku_feature_id': str(feature_id),
        'names': option_names
        }
        response = api_post(url, data)
        flash('Product sku option created successfully', 'success')
        return redirect(url_for('product.feature_show', id = feature_id))
    return render_template('product/option/new.html', feature_id = feature_id)
