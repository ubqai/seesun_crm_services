# -*- coding: utf-8 -*-
import os, datetime, random
from flask.helpers import make_response
from flask import flash, redirect, render_template, request, url_for, session
from . import app
from .models import *
from .product.api import *


@app.route('/mobile/index')
def mobile_index():
    return render_template('mobile/index.html')


# --- Case show, client content model ---
@app.route('/mobile/case_show')
def mobile_case_show():
    category = ContentCategory.query.filter(ContentCategory.name == '案例展示').first_or_404()
    classifications = category.classifications.order_by(ContentClassification.created_at.asc())
    return render_template('mobile/case_show.html', classifications = classifications)


@app.route('/mobile/case_classification/<int:id>')
def mobile_case_classification_show(id):
    classification = ContentClassification.query.get_or_404(id)
    return render_template('mobile/case_classification_show.html', classification = classification)


@app.route('/mobile/product_cases')
def mobile_product_cases():
    categories = load_categories()
    products_hash = {}
    for category in categories:
        products = load_products(category.get('category_id'))
        products_hash[category.get('category_id')] = products
    return render_template('mobile/product_cases.html', categories = categories, products_hash = products_hash)


@app.route('/mobile/product_case/<int:product_id>')
def mobile_product_case_show(product_id):
    product = load_product(product_id)
    case_ids = product.get('case_ids')
    contents = Content.query.filter(Content.id.in_(case_ids)).order_by(Content.created_at.desc())
    return render_template('mobile/product_case_show.html', product = product, contents = contents)


@app.route('/mobile/case_content/<int:id>')
def mobile_case_content_show(id):
    content = Content.query.get_or_404(id)
    return render_template('mobile/case_content_show.html', content = content)


# --- Product model ---
@app.route('/mobile/product')
def mobile_product():
    categories = load_categories()
    products_hash = {}
    for category in categories:
        products = load_products(category.get('category_id'))
        products_hash[category.get('category_id')] = products
    return render_template('mobile/product.html', categories =  categories, products_hash = products_hash)


@app.route('/mobile/product_show/<int:id>')
def mobile_product_show(id):
    product = load_product(id)
    return render_template('mobile/product_show.html', product = product)


# --- Storage model ---
@app.route('/mobile/share')
def mobile_share():
    return render_template('mobile/share.html')


@app.route('/mobile/share_storage_detail')
def mobile_share_storage_detail():
    return render_template('mobile/share_storage_detail.html')


@app.route('/mobile/share_storage_for_detail')
def mobile_share_storage_for_detail():
    return render_template('mobile/share_storage_for_detail.html')


@app.route('/mobile/share_storage_for_upload')
def mobile_share_storage_for_upload():
    return render_template('mobile/share_storage_for_upload.html')


@app.route('/mobile/share_storage_upload')
def mobile_share_storage_upload():
    return render_template('mobile/share_storage_upload.html')


@app.route('/mobile/storage')
def mobile_storage():
    categories = load_categories()
    products_hash = {}
    for category in categories:
        products = load_products(category.get('category_id'))
        products_hash[category.get('category_id')] = products
    return render_template('mobile/storage.html', categories=categories, products_hash=products_hash)


@app.route('/mobile/storage_show/<int:product_id>')
def mobile_storage_show(product_id):
    skus = load_skus(product_id)
    for sku in skus.get('skus'):
        sku['options'] = ','.join([','.join(list(option.values())) for option in sku.get('options')])
    return render_template('mobile/storage_show.html', skus=skus)


@app.route('/mobile/cart', methods=['GET', 'POST'])
def mobile_cart():
    order = []
    if 'order' in session:
        order = session['order']
    if request.method == 'POST':
        if request.form:
            for param in request.form:
                if 'number' in param and request.form.get(param):
                    index = param.rsplit('_', 1)[1]
                    order_content = {'product_name': request.form.get('product_name_%s' % index),
                                     # should be optimized later
                                     'sku_specification': request.form.get('sku_specification_%s' % index),
                                     'sku_code': request.form.get('sku_code_%s' % index),
                                     'sku_id': index,
                                     'number': int(request.form.get('number_%s' % index)),
                                     'square_num': "%.2f" % (0.3*int(request.form.get('number_%s' % index)))}
                    order.append(order_content)
        session['order'] = order
        return redirect(url_for('mobile_cart'))
    return render_template('mobile/cart.html', order=order)


@app.route('/mobile/create_order')
def mobile_create_order():
    if 'order' in session and session['order']:
        order_no = 'SS' + datetime.datetime.now().strftime('%y%m%d%H%M%S')
        user = User.query.first()
        buyer = request.args.get('buyer')
        buyer_company = request.args.get('buyer_company')
        buyer_address = request.args.get('buyer_address')
        order = Order(order_no=order_no, user=user, order_status='新订单',
                      order_memo=' ',
                      buyer_info={"buyer": buyer, "buyer_company": buyer_company,
                                  "buyer_address": buyer_address})
        db.session.add(order)
        for order_content in session['order']:
            oc = OrderContent(order=order, product_name=order_content.get('product_name'),
                              sku_specification=order_content.get('sku_specification'),
                              sku_code=order_content.get('sku_code'), number=order_content.get('number'),
                              square_num=order_content.get('square_num'))
            sku_id=order_content.get('sku_id')
            from .inventory.api import update_sku
            data = {"stocks_for_order": order_content.get('number')}
            response = update_sku(sku_id, data)
            if not response.status_code == 200:
                raise BaseException('error')
            db.session.add(oc)
        db.session.commit()
        # should modify sku stocks info meanwhile
        # call sku edit api
        session.pop('order', None)
        return redirect(url_for('mobile_created_orders'))
    else:
        return redirect(url_for('root'))


@app.route('/mobile/orders')
def mobile_orders():
    if 'order' in session and session['order']:
        return redirect(url_for('mobile_cart'))
    orders = Order.query.all()
    return render_template('mobile/orders.html', orders=orders)


@app.route('/mobile/created_orders')
def mobile_created_orders():
    orders = Order.query.all()
    return render_template('mobile/orders.html', orders=orders)


@app.route('/mobile/contract/<int:id>')
def mobile_contract_show(id):
    order = Order.query.get_or_404(id)
    contract = order.contracts.all()[0]
    return render_template('mobile/contract_show_mobile.html', order=order, contract=contract)


@app.route('/mobile/contract')
def mobile_contract():
    return render_template('mobile/contract.html')


# --- Project ---
@app.route('/mobile/project_lvl1')
def mobile_project_lvl1():
    return render_template('mobile/project_lvl1.html')


@app.route('/mobile/project_lvl2')
def mobile_project_lvl2():
    return render_template('mobile/project_lvl2.html')


# --- Design ---
@app.route('/mobile/design')
def mobile_design():
    return render_template('mobile/design.html')


# --- Material need ---
@app.route('/mobile/material_need')
def mobile_material_need():
    category = ContentCategory.query.filter(ContentCategory.name == '物料需要').first_or_404()
    classifications = category.classifications
    return render_template('mobile/material_need.html', classifications = classifications)

@app.route('/mobile/material_need_options/<int:classification_id>')
def mobile_material_need_options(classification_id):
    classification = ContentClassification.query.get_or_404(classification_id)
    options = classification.options
    return render_template('mobile/material_need_options.html', options = options)

@app.route('/mobile/material_need_contents/<int:option_id>')
def mobile_material_need_contents(option_id):
    option = ContentClassificationOption.query.get_or_404(option_id)
    contents = option.contents
    return render_template('mobile/material_need_contents.html', contents = contents)

@app.route('/mobile/material_application', methods = ['GET', 'POST'])
def mobile_material_application():
    if request.method == 'POST':
        return 'cc'
    return render_template('mobile/material_application.html')

@app.route('/mobile/material_lvl1')
def mobile_material_lvl1():
    return render_template('mobile/material_lvl1.html')


@app.route('/mobile/material_lvl2_for_apply')
def mobile_material_lvl2_for_apply():
    return render_template('mobile/material_lvl2_for_apply.html')


@app.route('/mobile/material_lvl2_for_download')
def mobile_material_lvl2_for_download():
    return render_template('mobile/material_lvl2_for_download.html')


@app.route('/mobile/material_lvl3')
def mobile_material_lvl3():
    return render_template('mobile/material_lvl3.html')


# --- Quick pay ---
@app.route('/mobile/quick_pay')
def mobile_quick_pay():
    return render_template('mobile/quick_pay.html')


@app.route('/mobile/quick_pay_lvl2')
def mobile_quick_pay_lvl2():
    return render_template('mobile/quick_pay_lvl2.html')


# --- Tracking info ---
@app.route('/mobile/tracking_lvl1')
def mobile_tracking_lvl1():
    return render_template('mobile/tracking_lvl1.html')


@app.route('/mobile/tracking_lvl2')
def mobile_tracking_lvl2():
    return render_template('mobile/tracking_lvl2.html')


# --- Verification ---
@app.route('/mobile/verification')
def mobile_verification():
    return render_template('mobile/verification.html')


# --- Construction guide ---
@app.route('/mobile/construction_guide')
def mobile_construction_guide():
    category = ContentCategory.query.filter(ContentCategory.name == '施工指导').first_or_404()
    classifications = category.classifications.order_by(ContentClassification.created_at.desc())
    return render_template('mobile/construction_guide.html', classifications = classifications)


@app.route('/mobile/construction_guide_options/<int:classification_id>')
def mobile_construction_guide_options(classification_id):
    classification = ContentClassification.query.get_or_404(classification_id)
    options = classification.options
    return render_template('mobile/construction_guide_options.html', options = options)


@app.route('/mobile/construction_guide_contents/<int:option_id>')
def mobile_construction_guide_contents(option_id):
    option = ContentClassificationOption.query.get_or_404(option_id)
    contents = option.contents
    return render_template('mobile/construction_guide_contents.html', contents = contents)


# --- After service ---
@app.route('/mobile/after_service')
def mobile_after_service():
    return render_template('mobile/after_service.html')


# --- CKEditor file upload ---
def gen_rnd_filename():
    filename_prefix = 'ck' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@app.route('/ckupload/', methods = ['POST'])
def ckupload():
    error = ''
    url = ''
    callback = request.args.get('CKEditorFuncNum')
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'upload/ckupload', rnd_name)
        # check file path exists or not
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename = '%s/%s' % ('upload/ckupload', rnd_name))
    else:
        error = 'post error'
    res = """
    <script type="text/javascript">
        window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>
    """ % (callback, url, error)
    response = make_response(res)
    response.headers['Content-Type'] = 'text/html'
    return response
