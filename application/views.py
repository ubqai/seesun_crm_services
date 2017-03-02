# -*- coding: utf-8 -*-
import os, datetime, random
from flask.helpers import make_response
from flask import flash, redirect, render_template, request, url_for, session
from . import app
from .models import *
from .product.api import *
import traceback
from .forms import *
from sqlalchemy import distinct

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
            user = User.query.first()
            application = MaterialApplication(app_no = 'MA' + datetime.datetime.now().strftime('%y%m%d%H%M%S'),
                user = user, status = '新申请')
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

# --- user service ---
@app.route('/mobile/users')
def mobile_users():
    return render_template('mobile/users.html')

@app.route('/mobile/users/dealers')
def mobile_users_dealers():
    return render_template('mobile/users_dealers.html')

@app.route('/mobile/users/dealers/new' , methods=['GET', 'POST'])
def mobile_users_dealers_new():
    app.logger.info("into mobile_users_dealers_new %s,[%s]" , request.method,request.form)
    if request.method == 'POST':
        try:
            form = UserDealerForm(request.form)

            app.logger.info("sales_range [%s]" , form.sales_range.data)
            if form.validate()==False:
                raise ValueError("")

            if User.query.filter_by(email=form.email.data).count()>0:
                raise ValueError("email已被注册,请更换!")

            # sah = SalesAreaHierarchy.query.filter_by(id=form.email.data).first()
            # if sah==None:
            #     raise ValueError("无此销售区域!")

            ui=UserInfo(name=form.name.data,telephone=form.phone.data,address=form.address.data,title=form.title.data)

            u=User(email=form.email.data,user_or_origin=2,nickname=form.nickname.data)

            u.user_infos.append(ui)
            for sah_id in form.sales_range.data:
                sah = SalesAreaHierarchy.query.filter_by(id=int(sah_id)).first()
                if sah==None:
                    raise ValueError("销售区域错误[%s]" % (sah_id))
                u.sales_areas.append(sah)

            db.session.add(u)
            db.session.commit()

            flash("添加经销商 %s,%s 成功" % (u.email,u.nickname))
            return render_template('mobile/users_dealers_search.html',form=UserDealerForm())
        except Exception as e:
            flash(e)
            print(traceback.print_exc())

            return render_template('mobile/users_dealers_new.html',form=form)
    else:
        form = UserDealerForm()
        return render_template('mobile/users_dealers_new.html',form=form)



@app.route('/mobile/users/dealers/edit/<int:user_id>' , methods=['GET', 'POST'])
def mobile_users_dealers_edit(user_id):
    if request.method == 'POST':
        try:
            form = UserDealerForm(request.form)
            u = User.query.filter_by(id=user_id).first()
            if u==None:
                raise ValueError("no user found!")

            app.logger.info("sales_range [%s]" , form.sales_range.data)
            if form.validate()==False:
                raise ValueError("")

            # sah = SalesAreaHierarchy.query.filter_by(id=form.email.data).first()
            # if sah==None:
            #     raise ValueError("无此销售区域!")
            u.email=form.email.data
            u.nickname=form.nickname.data

            if len(u.user_infos)==0:
                ui = UserInfo()
            else:
                ui = u.user_infos[0]

            ui.name=form.name.data
            ui.telephone=form.phone.data
            ui.address=form.address.data
            ui.title=form.title.data

            if len(u.user_infos)==0:
                u.user_infos.append(ui)

            if sorted([str(i.id) for i in u.sales_areas]) != sorted(form.sales_range.data):
                app.logger.info("reset sales_range")
                for sa in u.sales_areas:
                    u.sales_areas.remove(sa)
                for sah_id in form.sales_range.data:
                    app.logger.info("reset sales_range [%s]" % (sah_id))
                    sah = SalesAreaHierarchy.query.filter_by(id=int(sah_id)).first()
                    if sah==None:
                        raise ValueError("销售区域错误[%s]" % (sah_id))
                    u.sales_areas.append(sah)
            else:
                app.logger.info("same sales_range")


            db.session.add(u)
            db.session.commit()

            flash("修改经销商 %s,%s 成功" % (u.email,u.nickname))
            return render_template('mobile/users_dealers_search.html',form=UserDealerForm())
        except Exception as e:
            flash(e)
            print(traceback.print_exc())

            if u==None:
                return render_template('mobile/users_dealers_search.html',form=UserDealerForm())
            else:
                return render_template('mobile/users_dealers_edit.html',form=form,user_id=u.id)
    else:
        u=User.query.filter_by(id=user_id).first()
        form = UserDealerForm(obj=u)
        if len(u.user_infos)==0:
            pass
        else:
            ui=u.user_infos[0]
            form.name.data=ui.name
            form.address.data=ui.address
            form.phone.data=ui.telephone
            form.title.data=ui.title

        form.existed_sales_range.data='已选择销售范围 : '+','.join([i.name for i in u.sales_areas])
        form.sales_range.default=[str(i.id) for i in u.sales_areas]
        return render_template('mobile/users_dealers_edit.html',form=form,user_id=u.id)

@app.route('/mobile/users/dealers/search')
@app.route('/mobile/users/dealers/search/<int:page>')
def mobile_users_dealers_search(page=1):
    form=UserDealerForm(request.args)

    us = db.session.query(distinct(User.id)).filter(User.user_or_origin==2)
    if form.email.data:
        us = us.filter(User.email.like(form.email.data+"%"))
    if form.name.data:
        us = us.filter(User.nickname.like("%"+form.name.data+"%"))
    #how to search in many-to-many
    if form.sales_range.data and form.sales_range.data != ["-1"]:
        us=us.join(User.sales_areas).filter(SalesAreaHierarchy.id.in_(form.sales_range.data))

    us=User.query.filter(User.id.in_(us)).order_by(User.id)
    pagination = us.paginate(page, 10, False) 

    return render_template('mobile/users_dealers_search.html',users_dealers=pagination.items,pagination=pagination,form=form)


@app.route('/mobile/users/staffs')
def mobile_users_staffs():
    return render_template('mobile/users_staffs.html')

@app.route('/mobile/users/staffs/new' , methods=['GET', 'POST'])
def mobile_users_staffs_new():
    if request.method == 'POST':
        try:
            form = UserStaffForm(request.form)

            if form.validate()==False:
                raise ValueError("")

            if User.query.filter_by(email=form.email.data).count()>0:
                raise ValueError("email已被注册,请更换!")

            dh = DepartmentHierarchy.query.filter_by(id=form.dept_range.data).first()
            if dh==None:
                raise ValueError("无此部门!")

            ui=UserInfo(name=form.name.data,telephone=form.phone.data,address=form.address.data,title=form.title.data)

            u=User(email=form.email.data,user_or_origin=3,nickname=form.nickname.data)

            u.user_infos.append(ui)
            u.departments.append(dh)

            db.session.add(u)
            db.session.commit()

            flash("添加员工 %s,%s 成功" % (u.email,u.nickname))
            return render_template('mobile/users_staffs_search.html',form=UserStaffForm())
        except Exception as e:
            flash(e)
            print(traceback.print_exc())
            return render_template('mobile/users_staffs_new.html',form=form)
    else:
        form = UserStaffForm()
        return render_template('mobile/users_staffs_new.html',form=form)

@app.route('/mobile/users/staffs/edit/<int:user_id>' , methods=['GET', 'POST'])
def mobile_users_staffs_edit(user_id):
    app.logger.info("into mobile_users_staffs_edit and method : %s" % (request.method))
    if request.method == 'POST':
        try:
            form = UserStaffForm(request.form)
            app.logger.info("form info [%s]" % (request.form) )
            u = User.query.filter_by(id=user_id).first()
            if u==None:
                raise ValueError("no user found!")

            if form.validate()==False:
                raise ValueError("")

            dh = DepartmentHierarchy.query.filter_by(id=form.dept_range.data).first()
            if dh==None:
                raise ValueError("无此部门!")

            u.email=form.email.data
            u.nickname=form.nickname.data

            if len(u.user_infos)==0:
                ui = UserInfo()
            else:
                ui = u.user_infos[0]
            ui.name=form.name.data
            ui.telephone=form.phone.data
            ui.address=form.address.data
            ui.title=form.title.data

            if len(u.user_infos)==0:
                u.user_infos.append(ui)

            u.departments.remove(u.departments[0])
            u.departments.append(dh)

            db.session.add(u)
            db.session.commit()

            flash("修改员工 %s,%s 成功" % (u.email,u.nickname))
            return render_template('mobile/users_staffs_search.html')
        except Exception as e:
            flash(e)
            print(traceback.print_exc())
            if u==None:
                return render_template('mobile/users_staffs_search.html',form=UserStaffForm())
            else:
                return render_template('mobile/users_staffs_edit.html',form=form,user_id=u.id)
    else:
        u=User.query.filter_by(id=user_id).first()
        form = UserStaffForm(obj=u)
        if len(u.user_infos==0):
            pass
        else:
            ui=u.user_infos[0]
            form.name.data=ui.name
            form.address.data=ui.address
            form.phone.data=ui.telephone
            form.title.data=ui.title
        form.dept_range.choices= [(str(u.departments[0].id),u.departments[0].name)] + [(str(dh.id),dh.name) for dh in DepartmentHierarchy.query.all() ]
        return render_template('mobile/users_staffs_edit.html',form=form,user_id=u.id)

@app.route('/mobile/users/staffs/search')
@app.route('/mobile/users/staffs/search/<int:page>')
def mobile_users_staffs_search(page=1):
    form=UserStaffSearchForm(request.args)

    us = db.session.query(distinct(User.id)).filter(User.user_or_origin==3)
    if form.email.data:
        us = us.filter(User.email.like(form.email.data+"%"))
    if form.name.data:
        us = us.filter(User.nickname.like("%"+form.name.data+"%"))
    #how to search in many-to-many
    if form.dept_range.data and form.dept_range.data != "-1" :
        us=us.join(User.departments).filter(DepartmentHierarchy.id==form.dept_range.data)

    us=User.query.filter(User.id.in_(us)).order_by(User.id)
    pagination = us.paginate(page, 10, False) 

    return render_template('mobile/users_staffs_search.html',users_staffs=pagination.items,pagination=pagination,form=form)
