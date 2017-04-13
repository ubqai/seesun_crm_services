# -*- coding: utf-8 -*-
import os
import datetime
import random
import traceback
from flask.helpers import make_response
from flask import flash, redirect, render_template, request, url_for, session, current_app
from . import app
from .models import *
from .web_access_log.models import WebAccessLog, can_take_record
from .product.api import *
from .inventory.api import create_inventory, load_user_inventories
from .helpers import save_upload_file, resize_image_by_width
from flask_login import *
from .backstage_management.forms import AccountLoginForm
from .forms import *
from .wechat.models import WechatCall, WechatUserInfo
from .utils import is_number
from decimal import Decimal


@app.before_request
def web_access_log():
    # only take record of frontend access
    if can_take_record(request.path):
        try:
            record = WebAccessLog.take_record(request, current_user)
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            app.logger.warning('Exception: %s' % e)
            app.logger.warning(traceback.format_exc())
            db.session.rollback()
    pass


@app.route('/mobile/index')
def mobile_index():
    return render_template('mobile/index.html')


# --- Case show, client content model ---
@app.route('/mobile/case_show')
def mobile_case_show():
    category = ContentCategory.query.filter(ContentCategory.name == '案例展示').first_or_404()
    classifications = category.classifications.order_by(ContentClassification.created_at.asc())
    return render_template('mobile/case_show.html', classifications=classifications)


@app.route('/mobile/case_classification/<int:id>')
def mobile_case_classification_show(id):
    classification = ContentClassification.query.get_or_404(id)
    return render_template('mobile/case_classification_show.html', classification=classification)


@app.route('/mobile/product_cases')
def mobile_product_cases():
    categories = load_categories()
    products_hash = {}
    for category in categories:
        products = load_products(category.get('category_id'), only_valid=True)
        products_hash[category.get('category_id')] = products
    return render_template('mobile/product_cases.html', categories=categories, products_hash=products_hash)


@app.route('/mobile/product_case/<int:product_id>')
def mobile_product_case_show(product_id):
    product = load_product(product_id)
    case_ids = product.get('case_ids')
    contents = Content.query.filter(Content.id.in_(case_ids)).order_by(Content.created_at.desc())
    return render_template('mobile/product_case_show.html', product=product, contents=contents)


@app.route('/mobile/case_content/<int:id>')
def mobile_case_content_show(id):
    content = Content.query.get_or_404(id)
    return render_template('mobile/case_content_show.html', content=content)


# --- Product model ---
@app.route('/mobile/product')
def mobile_product():
    categories = load_categories()
    products_hash = {}
    for category in categories:
        products = load_products(category.get('category_id'), only_valid=True)
        products_hash[category.get('category_id')] = products
    return render_template('mobile/product.html', categories=categories, products_hash=products_hash)


@app.route('/mobile/product/<int:id>')
def mobile_product_show(id):
    product = load_product(id, option_sorted=True)
    skus = load_skus(id)
    contents = Content.query.filter(Content.id.in_(product.get('case_ids')))
    option_sorted = product.get('option_sorted')
    return render_template('mobile/product_show.html', product=product, skus=skus, contents=contents,
                           option_sorted=option_sorted)


# --- Storage model ---
@app.route('/mobile/share')
def mobile_share():
    return render_template('mobile/share.html')


@app.route('/mobile/share_storage_for_region')
def mobile_share_storage_for_region():
    regions = SalesAreaHierarchy.query.filter_by(level_grade=2).all()
    return render_template('mobile/share_storage_for_region.html', regions=regions)


@app.route('/mobile/share_storage_for_detail/<int:id>')
def mobile_share_storage_for_detail(id):
    areas = SalesAreaHierarchy.query.filter_by(level_grade=3, parent_id=id).all()
    return render_template('mobile/share_storage_for_detail.html', areas=areas)


@app.route('/mobile/storage')
def mobile_storage():
    categories = load_categories()
    products_hash = {}
    for category in categories:
        products = load_products(category.get('category_id'), only_valid=True)
        products_hash[category.get('category_id')] = products
    return render_template('mobile/storage.html', categories=categories, products_hash=products_hash)


@app.route("/mobile/storage_index")
def storage_index():
    return render_template('mobile/storage_index.html')


@app.route('/mobile/storage_show/<int:product_id>')
def mobile_storage_show(product_id):
    skus = load_skus(product_id)
    for sku in skus.get('skus'):
        sku['options'] = ','.join([','.join(list(option.values())) for option in sku.get('options')])
    return render_template('mobile/storage_show.html', skus=skus, product_id=product_id)


@app.route('/mobile/cart', methods=['GET', 'POST'])
def mobile_cart():
    order = []
    if 'order' in session:
        order = session['order']
    if request.method == 'POST':
        if request.form:
            for param in request.form:
                current_app.logger.info(param)
                if 'number' in param and request.form.get(param):
                    index = param.rsplit('_', 1)[1]
                    current_app.logger.info("%s-%s" % (index, request.form.get('number_%s' % index)))
                    if int(request.form.get('number_%s' % index)) > 0:
                        order_content = {'product_name': request.form.get('product_name_%s' % index),
                                         'sku_specification': request.form.get('sku_specification_%s' % index),
                                         'sku_code': request.form.get('sku_code_%s' % index),
                                         'sku_id': request.form.get('sku_id_%s' % index),
                                         'sku_thumbnail': request.form.get('sku_thumbnail_%s' % index),
                                         'batch_no': request.form.get('batch_no_%s' % index),
                                         'production_date': request.form.get('production_date_%s' % index),
                                         'batch_id': request.form.get('batch_id_%s' % index),
                                         'dealer': request.form.get('user_%s' % index),
                                         'number': int(request.form.get('number_%s' % index)),
                                         'square_num': "%.2f" % (0.3 * int(request.form.get('number_%s' % index)))}
                        order.append(order_content)
        session['order'] = order
        flash('成功加入购物车', 'success')
        if request.form.get('product_id') is not None:
            return redirect(url_for('mobile_storage_show', product_id=request.form.get('product_id')))
        elif request.form.get('area_id') is not None:
            return redirect(url_for('stocks_share_for_order', area_id=request.form.get('area_id')))
    return render_template('mobile/cart.html', order=order)


@app.route('/mobile/cart_delete/<int:sku_id>', methods=['GET', 'POST'])
def cart_delete(sku_id):
    sorders = session['order']
    for order_content in sorders:
        if order_content.get('sku_id') == str(sku_id):
            current_app.logger.info("delete")
            sorders.remove(order_content)
    session['order'] = sorders
    if len(session['order']) == 0:
        session.pop('order', None)
    if 'order' in session and session['order']:
        return redirect(url_for('mobile_cart'))
    else:
        return redirect(url_for('mobile_created_orders'))


@app.route('/mobile/create_order')
def mobile_create_order():
    if 'order' in session and session['order']:
        order_no = 'SS' + datetime.datetime.now().strftime('%y%m%d%H%M%S')
        buyer = request.args.get('buyer')
        buyer_company = request.args.get('buyer_company')
        buyer_address = request.args.get('buyer_address')
        contact_phone = request.args.get('contact_phone')
        contact_name = request.args.get('contact_name')
        project_name = request.args.get('project_name')
        dealer_name = request.args.get('dealer_name')
        province_id = current_user.sales_areas.first().parent_id
        us = db.session.query(User).join(User.departments).join(User.sales_areas).filter(
            User.user_or_origin == 3).filter(DepartmentHierarchy.name == "销售部").filter(
            SalesAreaHierarchy.id == province_id).first()
        if us is not None:
            sale_contract_id = us.id
            sale_contract = us.nickname
        else:
            sale_contract_id = None
            sale_contract = None
        order = Order(order_no=order_no, user=current_user, order_status='新订单',
                      order_memo=request.args.get('order_memo'),
                      sale_contract_id=sale_contract_id,
                      sale_contract=sale_contract,
                      buyer_info={"buyer": buyer, "buyer_company": buyer_company,
                                  "buyer_address": buyer_address, "contact_phone": contact_phone,
                                  "contact_name": contact_name, "project_name": project_name,
                                  "dealer_name": dealer_name})
        db.session.add(order)
        for order_content in session['order']:
            batch_info = {}
            if order_content.get('batch_id') is not None and order_content.get('batch_id') != '':
                batch_info = {'batch_no': order_content.get('batch_no'),
                              'production_date': order_content.get('production_date'),
                              'batch_id': order_content.get('batch_id'),
                              'dealer': order_content.get('dealer')
                              }
            oc = OrderContent(order=order, product_name=order_content.get('product_name'),
                              sku_specification=order_content.get('sku_specification'),
                              sku_code=order_content.get('sku_code'), number=order_content.get('number'),
                              square_num=order_content.get('number'), batch_info=batch_info
                              )
            sku_id = order_content.get('sku_id')
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
    return redirect(url_for('mobile_created_orders'))


@app.route('/mobile/created_orders')
def mobile_created_orders():
    page_size = int(request.args.get('page_size', 5))
    page_index = int(request.args.get('page', 1))
    orders_page = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()) \
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('mobile/orders.html', orders_page=orders_page)


@app.route('/mobile/contract/<int:id>')
def mobile_contract_show(id):
    order = Order.query.get_or_404(id)
    contract = order.contracts.all()[0]
    return render_template('mobile/contract_show_mobile.html', order=order, contract=contract)


# --- Design ---
@app.route('/mobile/design', methods=['GET', 'POST'])
def mobile_design():
    project_reports = ProjectReport.query.filter_by(status='项目报备审核通过')
    if request.method == 'POST':
        if request.form.get('filing_no') and request.files.get('ul_file'):
            project_report = ProjectReport.query.filter_by(report_no=request.form.get('filing_no')).first()
            if project_report in project_reports:
                file_path = save_upload_file(request.files.get('ul_file'))
                application = DesignApplication(filing_no=request.form.get('filing_no'),
                                                ul_file=file_path, status='新申请', applicant=current_user)
                application.save
                flash('产品设计申请提交成功', 'success')
                return redirect(url_for('mobile_design_applications'))
            else:
                flash('项目报备编号不存在', 'danger')
        else:
            flash('项目报备编号和上传设计图纸不能为空', 'danger')
        return redirect(url_for('mobile_design'))
    return render_template('mobile/design.html', project_reports=project_reports)


@app.route('/mobile/design_applications')
def mobile_design_applications():
    # list design applications of current user
    applications = current_user.design_applications
    return render_template('mobile/design_applications.html', applications=applications)


# --- Material need ---
@app.route('/mobile/material_need')
def mobile_material_need():
    category = ContentCategory.query.filter(ContentCategory.name == '物料需要').first_or_404()
    classifications = category.classifications
    return render_template('mobile/material_need.html', classifications=classifications)


@app.route('/mobile/material_need_options/<int:classification_id>')
def mobile_material_need_options(classification_id):
    classification = ContentClassification.query.get_or_404(classification_id)
    options = classification.options
    return render_template('mobile/material_need_options.html', options=options)


@app.route('/mobile/material_need_contents/<int:option_id>')
def mobile_material_need_contents(option_id):
    option = ContentClassificationOption.query.get_or_404(option_id)
    contents = option.contents
    return render_template('mobile/material_need_contents.html', contents=contents)


@app.route('/mobile/material_application/new', methods=['GET', 'POST'])
def mobile_material_application_new():
    if request.method == 'POST':
        app_contents = []
        if request.form:
            for param in request.form:
                if 'material' in param and request.form.get(param):
                    if int(request.form.get(param)) > 0:
                        app_contents.append([param.split('_', 1)[1], request.form.get(param)])
        if app_contents:
            application = MaterialApplication(app_no='MA' + datetime.datetime.now().strftime('%y%m%d%H%M%S'),
                                              user=current_user, status='新申请')
            db.session.add(application)
            for app_content in app_contents:
                material = Material.query.get_or_404(app_content[0])
                content = MaterialApplicationContent(material_name=material.name, number=app_content[1],
                                                     application=application)
                db.session.add(content)
            db.session.commit()
            flash('物料申请提交成功', 'success')
        else:
            flash('Please input correct number!', 'danger')
        return redirect(url_for('mobile_material_application_new'))
    materials = Material.query.all()
    return render_template('mobile/material_application_new.html', materials=materials)


@app.route('/mobile/material_applications')
def mobile_material_applications():
    applications = current_user.material_applications.order_by(MaterialApplication.created_at.desc())
    return render_template('mobile/material_applications.html', applications=applications)


@app.route('/mobile/material_application/<int:id>')
def mobile_material_application_show(id):
    application = MaterialApplication.query.get_or_404(id)
    if not application.user == current_user:
        return redirect(url_for('mobile_index'))
    return render_template('mobile/material_application_show.html', application=application)


@app.route('/mobile/material_application/<int:id>/reconfirm_accept')
def mobile_material_application_reconfirm_accept(id):
    application = MaterialApplication.query.get_or_404(id)
    if application.user != current_user or application.status != '等待经销商再次确认':
        return redirect(url_for('mobile_index'))
    application.status = '经销商已确认'
    db.session.add(application)
    db.session.commit()
    flash('已确认审核结果', 'success')
    return redirect(url_for('mobile_material_applications'))


@app.route('/mobile/material_application/<int:id>/cancel')
def mobile_material_application_cancel(id):
    application = MaterialApplication.query.get_or_404(id)
    if not application.user == current_user:
        return redirect(url_for('mobile_index'))
    application.status = '已取消'
    db.session.add(application)
    db.session.commit()
    flash('已取消申请', 'success')
    return redirect(url_for('mobile_material_applications'))


# --- Tracking info ---
@app.route('/mobile/tracking', methods=['GET', 'POST'])
def mobile_tracking():
    if request.method == 'POST':
        contract_no = request.form.get('contract_no').strip()
        receiver_tel = request.form.get('receiver_tel').strip()
        tracking_info = TrackingInfo.query.filter(
            (TrackingInfo.contract_no == contract_no) &
            (TrackingInfo.receiver_tel == receiver_tel)
        ).first()
        if tracking_info:
            return redirect(url_for('mobile_tracking_info', id=tracking_info.id))
        else:
            flash('未找到对应物流信息', 'warning')
            return redirect(url_for('mobile_tracking'))
    contracts = Contract.query.filter_by(user_id=current_user.id).all()
    tracking_infos = TrackingInfo.query.filter(
        TrackingInfo.contract_no.in_([contract.contract_no for contract in contracts])).all()
    return render_template('mobile/tracking.html', tracking_infos=tracking_infos)


@app.route('/mobile/tracking_info/<int:id>')
def mobile_tracking_info(id):
    delivery_infos_dict = {
        'recipient': '收货人',
        'tracking_no': '物流单号',
        'delivery_tel': '货运公司电话',
        'goods_weight': '货物重量(kg)',
        'goods_count': '货物件数',
        'duration': '运输时间',
        'freight': '运费(元)',
        'pickup_no': '提货号码'
    }
    tracking_info = TrackingInfo.query.get_or_404(id)
    return render_template('mobile/tracking_info.html', tracking_info=tracking_info)


# --- Construction guide ---
@app.route('/mobile/construction_guide')
def mobile_construction_guide():
    category = ContentCategory.query.filter(ContentCategory.name == '施工指导').first_or_404()
    classifications = category.classifications.order_by(ContentClassification.created_at.desc())
    return render_template('mobile/construction_guide.html', classifications=classifications)


@app.route('/mobile/construction_guide_options/<int:classification_id>')
def mobile_construction_guide_options(classification_id):
    classification = ContentClassification.query.get_or_404(classification_id)
    options = classification.options
    return render_template('mobile/construction_guide_options.html', options=options)


@app.route('/mobile/construction_guide_contents/<int:option_id>')
def mobile_construction_guide_contents(option_id):
    option = ContentClassificationOption.query.get_or_404(option_id)
    contents = option.contents
    return render_template('mobile/construction_guide_contents.html', contents=contents)


# --- After service ---
@app.route('/mobile/after_service')
def mobile_after_service():
    return render_template('mobile/after_service.html')


# --- CKEditor file upload ---
def gen_rnd_filename():
    filename_prefix = 'ck' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@app.route('/ckupload/', methods=['POST'])
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
            resize_image_by_width(filepath, new_width=640)
            url = url_for('static', filename='%s/%s' % ('upload/ckupload', rnd_name))
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


# --- Project ---
@app.route('/mobile/project_report/new', methods=['GET', 'POST'])
def new_project_report():
    if request.method == 'POST':
        report_content = {"buyer": request.form.get("buyer"),
                          "buyer_company": request.form.get("buyer_company"),
                          "buyer_address": request.form.get("buyer_address"),
                          "project_name": request.form.get("project_name"),
                          "product_series": request.form.get("product_series"),
                          "contact_phone": request.form.get("contact_phone"),
                          "contact_name": request.form.get("contact_name"),
                          "project_memo": request.form.get("project_memo")}
        project_report = ProjectReport(
            app_id=current_user.id,
            status="新创建待审核",
            report_no="PR%s" % datetime.datetime.now().strftime('%y%m%d%H%M%S'),
            report_content=report_content
        )
        db.session.add(project_report)
        db.session.commit()
        return redirect(url_for('project_report_index'))
    return render_template('mobile/project_report_new.html')


@app.route('/mobile/project_report/index', methods=['GET'])
def project_report_index():
    page_size = int(request.args.get('page_size', 5))
    page_index = int(request.args.get('page', 1))
    project_reports = ProjectReport.query.filter_by(app_id=current_user.id).order_by(ProjectReport.created_at.desc()) \
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('mobile/project_report_index.html', project_reports=project_reports)


@app.route('/mobile/project_report/<int:id>', methods=['GET'])
def project_report_show(id):
    project_report = ProjectReport.query.get_or_404(id)
    return render_template('mobile/project_report_show.html', project_report=project_report)


@app.route('/mobile/share_index/<int:area_id>', methods=['GET'])
def stocks_share(area_id):
    categories = load_categories()
    if area_id == 0:
        users = [current_user]
    else:
        area = SalesAreaHierarchy.query.get_or_404(area_id)
        users = area.users.all()
        for sarea in SalesAreaHierarchy.query.filter_by(parent_id=area.id).all():
            users.extend(sarea.users.all())
            for ssarea in SalesAreaHierarchy.query.filter_by(parent_id=sarea.id).all():
                users.extend(ssarea.users.all())
    return render_template('mobile/share_index.html', categories=categories, users=users)


@app.route('/mobile/share_index_for_order/<int:area_id>', methods=['GET'])
def stocks_share_for_order(area_id):
    categories = load_categories()
    if area_id == 0:
        users = [current_user]
    else:
        area = SalesAreaHierarchy.query.get_or_404(area_id)
        users = area.users.all()
        for sarea in SalesAreaHierarchy.query.filter_by(parent_id=area.id).all():
            users.extend(sarea.users.all())
            for ssarea in SalesAreaHierarchy.query.filter_by(parent_id=sarea.id).all():
                users.extend(ssarea.users.all())
    batch_infos = []
    # 经销商库存
    for user in users:
        for category in categories:
            if request.args.get("category_name", '') == '' or \
                    (request.args.get("category_name", '') != '' and category.get('category_name') == request.args.get(
                        "category_name")):
                products_json = load_products(category.get('category_id'), only_valid=True)
                if len(products_json) > 0:
                    for product_json in products_json:
                        if not product_json.get('isvalid') == "NO":
                            skus_json = load_skus(product_json.get('product_id'))
                            if len(skus_json.get('skus')) > 0:
                                for sku in skus_json.get('skus'):
                                    if not sku.get('isvalid') == "NO":
                                        sku_option = ""
                                        for option in sku.get('options'):
                                            for key, value in option.items():
                                                sku_option = "%s %s" % (sku_option, value)
                                        if request.args.get("sku_code", '') == '' or \
                                                (request.args.get("sku_code", '') != '' and sku.get(
                                                    'code') == request.args.get("sku_code")):
                                            invs = load_user_inventories(user.id, sku.get('sku_id'), "2")
                                            for inv in invs:
                                                for batch in inv.get('batches'):
                                                    batch_infos.append({"product_name": product_json.get('name'),
                                                                        "category_name": category.get('category_name'),
                                                                        "sku_specification": sku_option,
                                                                        "thumbnail": sku.get('thumbnail'),
                                                                        "user": user.nickname,
                                                                        "city": "%s工程剩余库存" % user.sales_areas.first().name,
                                                                        "sku_id": sku.get('sku_id'),
                                                                        "production_date": batch.get('production_date'),
                                                                        "batch_no": batch.get('batch_no'),
                                                                        "batch_id": batch.get('inv_id'),
                                                                        "sku_code": sku.get('code'),
                                                                        "price": batch.get('price'),
                                                                        "stocks": batch.get('stocks')})
    # 公司库存
    for category in categories:
        if request.args.get("category_name", '') == '' or \
                (request.args.get("category_name", '') != '' and category.get('category_name') == request.args.get(
                    "category_name")):
            products_json = load_products(category.get('category_id'), only_valid=True)
            if len(products_json) > 0:
                for product_json in products_json:
                    if not product_json.get('isvalid') == "NO":
                        skus_json = load_skus(product_json.get('product_id'))
                        if len(skus_json.get('skus')) > 0:
                            for sku in skus_json.get('skus'):
                                if not sku.get('isvalid') == "NO":
                                    sku_option = ""
                                    for option in sku.get('options'):
                                        for key, value in option.items():
                                            sku_option = "%s %s" % (sku_option, value)
                                    if request.args.get("sku_code", '') == '' or \
                                            (request.args.get("sku_code", '') != '' and sku.get(
                                                'code') == request.args.get("sku_code")):
                                        invs = load_user_inventories("0", sku.get('sku_id'), "2")
                                        for inv in invs:
                                            for batch in inv.get('batches'):
                                                batch_infos.append({"product_name": product_json.get('name'),
                                                                    "category_name": category.get('category_name'),
                                                                    "sku_specification": sku_option,
                                                                    "thumbnail": sku.get('thumbnail'),
                                                                    "user": "公司",
                                                                    "city": "公司工程剩余库存",
                                                                    "sku_id": sku.get('sku_id'),
                                                                    "production_date": batch.get('production_date'),
                                                                    "batch_no": batch.get('batch_no'),
                                                                    "batch_id": batch.get('inv_id'),
                                                                    "sku_code": sku.get('code'),
                                                                    "price": batch.get('price'),
                                                                    "stocks": batch.get('stocks')})
    return render_template('mobile/share_index_for_order.html', batch_infos=batch_infos, area_id=area_id,
                           categories=categories)


@app.route('/mobile/upload_share_index', methods=['GET'])
def upload_share_index():
    categories = load_categories()
    return render_template('mobile/upload_share_index.html', categories=categories)


@app.route('/mobile/new_share_inventory/<product_name>/<sku_id>', methods=['GET', 'POST'])
def new_share_inventory(product_name, sku_id):
    if request.method == 'POST':
        params = {
            'production_date': request.form.get('production_date', ''),
            'stocks': request.form.get('stocks', ''),
            'price': request.form.get('price')
        }
        production_date = request.form.get('production_date', '')
        price = request.form.get('price')
        stocks = request.form.get('stocks', '')
        if production_date == '':
            flash('生产日期不能为空', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        if stocks == '':
            flash('库存数量不能为空', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        if not is_number(stocks):
            flash('库存数量必须为数字', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        if Decimal(stocks) < Decimal("1"):
            flash('库存数量不能小于1', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        if price == '':
            flash('价格不能为空', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        if not is_number(price):
            flash('价格必须为数字', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        if Decimal(price) <= Decimal("0"):
            flash('价格必须大于0', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        upload_files = request.files.getlist('pic_files[]')
        filenames = []
        for file in upload_files:
            file_path = save_upload_file(file)
            filenames.append(file_path)
        if filenames == [None]:
            flash('材料图片必须上传', 'danger')
            return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name,
                                   params=params)
        sku = get_sku(sku_id)
        options = []
        for option in sku.get('options'):
            for key, value in option.items():
                options.append(value)
        si = ShareInventory(
            applicant_id=current_user.id,
            status="新申请待审核",
            batch_no='BT%s%s' % (datetime.datetime.now().strftime('%y%m%d%H%M%S'), 2),
            product_name=product_name,
            sku_id=sku_id,
            sku_code=sku.get('code'),
            sku_option=" ".join(options),
            production_date=production_date,
            stocks=stocks,
            price=price,
            pic_files=filenames
        )
        db.session.add(si)
        db.session.commit()
        flash('已申请，等待审核', 'success')
        return redirect(url_for('share_inventory_list'))
    return render_template('mobile/new_share_inventory.html', sku_id=sku_id, product_name=product_name, params={})


@app.route('/mobile/share_inventory_list', methods=['GET'])
def share_inventory_list():
    page_size = int(request.args.get('page_size', 5))
    page_index = int(request.args.get('page', 1))
    sis = ShareInventory.query.filter_by(applicant_id=current_user.id).order_by(ShareInventory.created_at.desc()) \
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('mobile/share_inventory_list.html', sis=sis)


# --- mobile user---
@app.route('/mobile/user/login', methods=['GET', 'POST'])
def mobile_user_login():
    if current_user.is_authenticated:
        if current_user.user_or_origin == 2:
            app.logger.info("已登入用户[%s],重定向至mobile_index" % (current_user.nickname))
            return redirect(url_for('mobile_index'))
        else:
            # 不运行前后端同时登入在一个WEB上
            app.logger.info("后台用户[%s]自动登出,[%s][%s]" % (current_user.nickname, request.path, request.endpoint))
            logout_user()

    if request.method == 'POST':
        try:
            form = AccountLoginForm(request.form, meta={'csrf_context': session})
            if form.validate() is False:
                raise ValueError("")

            # 微信只能经销商登入
            user = User.login_verification(form.email.data, form.password.data, 2)
            if user is None:
                raise ValueError("用户名或密码错误")

            login_valid_errmsg = user.check_can_login()
            if not login_valid_errmsg == "":
                raise ValueError(login_valid_errmsg)

            login_user(user)
            app.logger.info("mobile login success [%s]" % (user.nickname))
            # 直接跳转至需访问页面
            if session.get("login_next_url"):
                next_url = session.pop("login_next_url")
            else:
                next_url = url_for('mobile_index')
            return redirect(next_url)
        except Exception as e:
            app.logger.info("mobile login failure [%s]" % (e))
            flash(e)
            return render_template('mobile/user_login.html', form=form)
    else:
        # 已在拦截中处理
        # if request.args.get("code") is not None:
        #     try:
        #         openid = WechatCall.get_open_id_by_code(request.args.get("code"))
        #         wui = WechatUserInfo.query.filter_by(open_id=openid, is_active=True).first()
        #         if wui is not None:
        #             exists_binding_user = User.query.filter_by(id=wui.user_id).first()
        #             if exists_binding_user is not None:
        #                 login_user(exists_binding_user)
        #                 app.logger.info("binding user login [%s] - [%s]" % (openid, exists_binding_user.nickname))
        #                 return redirect(url_for('mobile_index'))
        #     except Exception:
        #         pass

        form = AccountLoginForm(meta={'csrf_context': session})
        return render_template('mobile/user_login.html', form=form)


@app.route('/mobile/user/logout')
def mobile_user_logout():
    logout_user()
    return redirect(url_for('mobile_user_login'))


@app.route('/mobile/user/info/<int:user_id>')
def mobile_user_info(user_id):
    if user_id != current_user.id:
        flash("非法提交,请通过正常页面进入")
        return redirect(url_for('mobile_index'))

    u = User.query.filter_by(id=user_id).first()
    if u is None:
        return redirect(url_for('mobile_index'))

    form = UserInfoForm(obj=u, user_type=u.user_or_origin, meta={'csrf_context': session})

    if len(u.user_infos) == 0:
        pass
    else:
        ui = u.user_infos[0]
        form.name.data = ui.name
        form.address.data = ui.address
        form.phone.data = ui.telephone
        form.title.data = ui.title

    if u.sales_areas.first() is not None:
        form.sale_range.data = u.sales_areas.first().name

    return render_template('mobile/user_info.html', form=form)


@app.route('/mobile/user/password_update', methods=['POST'])
def mobile_user_password_update():
    app.logger.info("into mobile_user_password_update")
    try:
        form = BaseCsrfForm(request.form, meta={'csrf_context': session})
        if form.validate() is False:
            raise ValueError("非法提交,请通过正常页面进行修改")

        if request.form.get("email") != current_user.email:
            raise ValueError("非法提交,请通过正常页面进行修改")

        User.update_password(request.form.get("email"),
                             request.form.get("password_now"),
                             request.form.get("password_new"),
                             request.form.get("password_new_confirm"),
                             current_user.user_or_origin)

        for wui in WechatUserInfo.query.filter_by(user_id=current_user.id, is_active=True).all():
            wui.is_active = False
            wui.save()

        flash("密码修改成功,如有绑定微信帐号,需要重新绑定")
    except Exception as e:
        flash("密码修改失败: %s" % e)

    return redirect(url_for('mobile_user_info', user_id=current_user.id))
