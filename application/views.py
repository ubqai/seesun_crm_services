# -*- coding: utf-8 -*-
import os, datetime, random
from flask.helpers import make_response
from flask import flash, redirect, render_template, request, url_for, session
from . import app
from .models import *
from .product.api import *
from .inventory.api import create_inventory
from .helpers import save_upload_file
from flask_login import *
from .organization.forms import UserLoginForm
from .forms import *


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


@app.route('/mobile/product/<int:id>')
def mobile_product_show(id):
    product  = load_product(id, option_sorted = True)
    skus     = load_skus(id)
    contents = Content.query.filter(Content.id.in_(product.get('case_ids')))
    option_sorted = product.get('option_sorted')
    return render_template('mobile/product_show.html', product = product, skus = skus, contents = contents, 
        option_sorted = option_sorted)


# --- Storage model ---
@app.route('/mobile/share')
def mobile_share():
    return render_template('mobile/share.html')


@app.route('/mobile/share_storage_detail')
def mobile_share_storage_detail():
    return render_template('mobile/share_storage_detail.html')


@app.route('/mobile/share_storage_for_detail')
def mobile_share_storage_for_detail():
    areas = SalesAreaHierarchy.query.filter_by(level_grade=3).all()
    return render_template('mobile/share_storage_for_detail.html', areas=areas)


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
    return render_template('mobile/storage_show.html', skus=skus, product_id=product_id)


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
                    if int(request.form.get('number_%s' % index)) > 0:
                        order_content = {'product_name': request.form.get('product_name_%s' % index),
                                         'sku_specification': request.form.get('sku_specification_%s' % index),
                                         'sku_code': request.form.get('sku_code_%s' % index),
                                         'sku_id': index,
                                         'number': int(request.form.get('number_%s' % index)),
                                         'square_num': "%.2f" % (0.3*int(request.form.get('number_%s' % index)))}
                        order.append(order_content)
        session['order'] = order
        flash('成功加入购物车', 'success')
        return redirect(url_for('mobile_storage_show', product_id=request.form.get('product_id')))
    return render_template('mobile/cart.html', order=order)


@app.route('/mobile/create_order')
def mobile_create_order():
    if 'order' in session and session['order']:
        order_no = 'SS' + datetime.datetime.now().strftime('%y%m%d%H%M%S')
        buyer = request.args.get('buyer')
        buyer_company = request.args.get('buyer_company')
        buyer_address = request.args.get('buyer_address')
        company_name = request.args.get('company_name')
        project_address = request.args.get('project_address')
        contact_phone = request.args.get('contact_phone')
        contact_name = request.args.get('contact_name')
        order = Order(order_no=order_no, user=current_user, order_status='新订单',
                      order_memo=' ',
                      buyer_info={"buyer": buyer, "buyer_company": buyer_company,
                                  "buyer_address": buyer_address, "contact_phone": contact_phone,
                                  "contact_name": contact_name, "company_name": company_name,
                                  "project_address": project_address})
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
    orders = Order.query.filter_by(user_id=current_user.id).all()
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
@app.route('/mobile/design', methods = ['GET', 'POST'])
def mobile_design():
    project_reports = ProjectReport.query.filter_by(status='项目报备审核通过')
    if request.method == 'POST':
        if request.form.get('filing_no') and request.files.get('ul_file'):
            project_report = ProjectReport.query.filter_by(report_no = request.form.get('filing_no')).first()
            if project_report in project_reports:
                file_path = save_upload_file(request.files.get('ul_file'))
                application = DesignApplication(filing_no = request.form.get('filing_no'), 
                    ul_file = file_path, status = '新申请', applicant = current_user)
                application.save
                flash('产品设计申请提交成功', 'success')
                return redirect(url_for('mobile_design_applications'))
            else:
                flash('项目报备编号不存在', 'danger')
        else:
            flash('项目报备编号和上传设计图纸不能为空', 'danger')
        return redirect(url_for('mobile_design'))
    return render_template('mobile/design.html', project_reports = project_reports)


@app.route('/mobile/design_applications')
def mobile_design_applications():
    # list design applications of current user
    applications = current_user.design_applications #DesignApplication.query.all()
    return render_template('mobile/design_applications.html', applications = applications)


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


@app.route('/mobile/material_application/new', methods = ['GET', 'POST'])
def mobile_material_application_new():
    if request.method == 'POST':
        app_contents = []
        if request.form:
            for param in request.form:
                if 'material' in param and request.form.get(param):
                    if int(request.form.get(param)) > 0:
                        app_contents.append([param.split('_',1)[1], request.form.get(param)])
        if app_contents:
            application = MaterialApplication(app_no = 'MA' + datetime.datetime.now().strftime('%y%m%d%H%M%S'),
                user = current_user, status = '新申请')
            db.session.add(application)
            for app_content in app_contents:
                content = MaterialApplicationContent(material_id = app_content[0], number = app_content[1], 
                    application = application)
                db.session.add(content)
            db.session.commit()
            flash('物料申请提交成功', 'success')
        else:
            flash('Please input correct number!', 'danger')
        return redirect(url_for('mobile_material_application_new'))
    materials = Material.query.all()
    return render_template('mobile/material_application_new.html', materials = materials)


@app.route('/mobile/material_applications')
def mobile_material_applications():
    applications = MaterialApplication.query.all()
    return render_template('mobile/material_applications.html', applications = applications)


@app.route('/mobile/material_application/<int:id>')
def mobile_material_application_show(id):
    application = MaterialApplication.query.get_or_404(id)
    return render_template('mobile/material_application_show.html', application = application)


# --- Quick pay --- not be used anymore
@app.route('/mobile/quick_pay')
def mobile_quick_pay():
    return render_template('mobile/quick_pay.html')


@app.route('/mobile/quick_pay_lvl2')
def mobile_quick_pay_lvl2():
    return render_template('mobile/quick_pay_lvl2.html')


# --- Tracking info ---
@app.route('/mobile/tracking', methods = ['GET', 'POST'])
def mobile_tracking():
    if request.method == 'POST':
        contract_no = request.form.get('contract_no').strip()
        receiver_tel = request.form.get('receiver_tel').strip()
        tracking_info = TrackingInfo.query.filter(
            (TrackingInfo.contract_no == contract_no) &
            (TrackingInfo.receiver_tel == receiver_tel)
            ).first()
        if tracking_info:
            return redirect(url_for('mobile_tracking_info', id = tracking_info.id))
        else:
            flash('未找到对应物流信息', 'warning')
            return redirect(url_for('mobile_tracking'))
    return render_template('mobile/tracking.html')


@app.route('/mobile/tracking_info/<int:id>')
def mobile_tracking_info(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    return render_template('mobile/tracking_info.html', tracking_info = tracking_info)


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

@app.route('/mobile/project_report/new', methods=['GET', 'POST'])
def new_project_report():
    if request.method == 'POST':
        report_content = {"app_company": request.form.get("app_company"),
                          "project_follower": request.form.get("project_follower"),
                          "contract_phone": request.form.get("contract_phone"),
                          "contract_fax": request.form.get("contract_fax"),
                          "project_name": request.form.get("project_name"),
                          "report_date": request.form.get("report_date"),
                          "project_address": request.form.get("project_address"),
                          "project_area": request.form.get("project_area"),
                          "product_place": request.form.get("product_place"),
                          "recommended_product_line": request.form.get("recommended_product_line"),
                          "recommended_product_color": request.form.get("recommended_product_color"),
                          "project_completion_time": request.form.get("project_completion_time"),
                          "expected_order_time": request.form.get("expected_order_time"),
                          "competitive_brand_situation": request.form.get("competitive_brand_situation"),
                          "project_owner": request.form.get("project_owner"),
                          "project_decoration_total": request.form.get("project_decoration_total"),
                          "project_design_company": request.form.get("project_design_company"),
                          "is_authorization_needed": request.form.get("is_authorization_needed"),
                          "expected_authorization_date": request.form.get("expected_authorization_date"),
                          "authorize_company_name": request.form.get('authorize_company_name')}
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
    project_reports = ProjectReport.query.filter_by(app_id=current_user.id).all()
    return render_template('mobile/project_report_index.html', project_reports=project_reports)


@app.route('/mobile/project_report/<int:id>', methods=['GET'])
def project_report_show(id):
    project_report = ProjectReport.query.get_or_404(id)
    return render_template('mobile/project_report_show.html', project_report=project_report)


@app.route('/mobile/share_index/<int:area_id>', methods=['GET'])
def stocks_share(area_id):
    categories = load_categories()
    area = SalesAreaHierarchy.query.get_or_404(area_id)
    users = area.users.all()
    for sarea in SalesAreaHierarchy.query.filter_by(parent_id=area.id).all():
        users.extend(sarea.users.all())
        for ssarea in SalesAreaHierarchy.query.filter_by(parent_id=sarea.id).all():
            users.extend(ssarea.users.all())
    return render_template('mobile/share_index.html', categories=categories, users=users)


@app.route('/mobile/upload_share_index', methods=['GET'])
def upload_share_index():
    categories = load_categories()
    return render_template('mobile/upload_share_index.html', categories=categories)


@app.route('/mobile/new_share_inventory/<int:id>', methods=['GET', 'POST'])
def new_share_inventory(id):
    if request.method == 'POST':
        user_id = current_user.id
        production_date = request.form.get('production_date')
        batch_no = request.form.get('batch_no')
        stocks = request.form.get('stocks')
        inv_type = 2
        user_name = current_user.nickname
        if stocks is None:
            flash('库存数量不能为空', 'danger')
            return render_template('mobile/new_share_inventory.html', id=id)
        elif int(stocks) < 1:
            flash('库存数量不能小于1', 'danger')
            return render_template('mobile/new_share_inventory.html', id=id)
        data = {'inventory_infos': [{"sku_id": id, "inventory": [{"type": inv_type, "user_id": user_id,
                                                                  "user_name": user_name,
                                                                  "production_date": production_date,
                                                                  "valid_until": production_date,
                                                                  "batch_no": batch_no,
                                                                  "stocks": stocks}]}]}
        response = create_inventory(data)
        if response.status_code == 201:
            flash('库存共享成功', 'success')
        else:
            flash('库存共享失败', 'danger')
        return redirect(url_for('stocks_share'))
    return render_template('mobile/new_share_inventory.html', id=id)


# --- mobile user---
@app.route('/mobile/user/login', methods=['GET', 'POST'])
def mobile_user_login():
    if current_user.is_authenticated:
        if current_user.user_or_origin==2:
            return redirect(url_for('mobile_index'))

    if request.method == 'POST':
        try:
            #不运行前后端同时登入在一个WEB上
            if current_user.is_authenticated and current_user.user_or_origin!=3:
                app.logger.info("后台用户[%s]自动登出" % (current_user.nickname))
                logout_user()

            form = UserLoginForm(request.form)
            if form.validate()==False:
                raise ValueError("")

            #后台只能员工登入
            user=User.login_verification(form.email.data,form.password.data,2)
            if user==None:
                raise ValueError("用户名或密码错误")
            if not user.is_active():
                raise ValueError("用户异常,请联系管理员")
                
            login_user(user)
            app.logger.info("mobile login success [%s]" % (user.nickname))
            return redirect(url_for('mobile_index'))
        except Exception as e:
            app.logger.info("mobile login failure [%s]" % (e))
            flash(e)
    else:
        form = UserLoginForm()

    return render_template('mobile/user_login.html',form=form)

@app.route('/mobile/user/info/<int:user_id>')
def mobile_user_info(user_id):
    u=User.query.filter_by(id=user_id).first()
    if u==None:
        return redirect(url_for('mobile_index'))

    form = UserInfoForm(obj=u,user_type=u.user_or_origin)

    if len(u.user_infos)==0:
        pass
    else:
        ui=u.user_infos[0]
        form.name.data=ui.name
        form.address.data=ui.address
        form.phone.data=ui.telephone
        form.title.data=ui.title

    if u.sales_areas.first()!=None:
        form.sale_range.data=u.sales_areas.first().name
    if u.departments.first()!=None:
        form.dept_ranges.data=",".join([d.name for d in u.departmets.all()])

    return render_template('mobile/user_info.html',form=form)
