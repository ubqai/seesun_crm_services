# -*- coding: utf-8 -*-
import json
import base64
from flask import Blueprint, flash, redirect, render_template, url_for, request, send_file, current_app
from flask.helpers import make_response
from .. import app, cache
from ..models import *
from ..helpers import object_list, gen_qrcode, gen_random_string, delete_file
from .forms import ContractForm, TrackingInfoForm1, TrackingInfoForm2, UserSearchForm
from ..inventory.api import load_inventories_by_code, update_sku_by_code
from application.utils import is_number
from decimal import Decimal
from flask_login import current_user
from ..wechat.models import WechatCall
from ..utils import add_months
from functools import reduce

order_manage = Blueprint('order_manage', __name__, template_folder='templates')


@order_manage.route("/orders", methods=['GET'])
def order_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    orders_page = Order.query.filter(
        Order.user_id.in_(set([user.id for user in current_user.get_subordinate_dealers()]))).order_by(
        Order.created_at.desc()).paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/index.html', orders_page=orders_page)


@order_manage.route("/orders/<int:id>", methods=['GET'])
def order_show(id):
    order = Order.query.get_or_404(id)
    return render_template('order_manage/show.html', order=order)


@order_manage.route("/orders/<int:id>/cancel", methods=['GET'])
def order_cancel(id):
    order = Order.query.get_or_404(id)
    order.order_status = "订单取消"
    db.session.add(order)
    db.session.commit()
    return redirect(url_for("order_manage.order_index"))


@order_manage.route("/orders/<int:id>/new_contract", methods=['GET', 'POST'])
def contract_new(id):
    order = Order.query.get_or_404(id)
    '''
    form = ContractForm(amount=request.form.get("amount"),
                        delivery_time=request.form.get("delivery_time"),
                        offer_no=request.form.get("offer_no"),
                        logistics_costs=request.form.get('logistics_costs'),
                        live_floor_costs=request.form.get('live_floor_costs'),
                        self_leveling_costs=request.form.get('self_leveling_costs'),
                        crossed_line_costs=request.form.get('crossed_line_costs'),
                        sticky_costs=request.form.get('sticky_costs'),
                        full_adhesive_costs=request.form.get('full_adhesive_costs'),
                        material_loss_percent=request.form.get('material_loss_percent'),
                        other_costs=request.form.get('other_costs'),
                        tax_costs=request.form.get('tax_costs'))
    '''
    if request.method == 'POST':
        params = {
            "amount": request.form.get("amount"),
            "delivery_time": request.form.get("delivery_time"),
            "logistics_costs": request.form.get('logistics_costs'),
            "live_floor_costs": request.form.get('live_floor_costs'),
            "self_leveling_costs": request.form.get('self_leveling_costs'),
            "crossed_line_costs": request.form.get('crossed_line_costs'),
            "sticky_costs": request.form.get('sticky_costs'),
            "full_adhesive_costs": request.form.get('full_adhesive_costs'),
            "material_loss_percent": request.form.get('material_loss_percent'),
            "other_costs": request.form.get('other_costs'),
            "tax_costs": request.form.get('tax_costs'),
            "tax_price": request.form.get('tax_price')
        }
        if not is_number(request.form.get("amount")):
            flash('总金额必须为数字', 'warning')
            return render_template('order_manage/contract_new.html', order=order, params=params)
        current_app.logger.info(request.form.get("delivery_time"))
        if request.form.get("delivery_time") is None or request.form.get("delivery_time") == '':
            flash('交货期必须填写', 'warning')
            return render_template('order_manage/contract_new.html', order=order, params=params)
        if not request.form.get("tax_costs", '') == '':
            if not is_number(request.form.get("tax_costs")):
                flash('税点必须为0-100之间的数字', 'warning')
                return render_template('order_manage/contract_new.html', order=order, params=params)
            if Decimal(request.form.get("tax_costs")) > Decimal("100") or Decimal(request.form.get("tax_costs")) < Decimal("0"):
                flash('税点必须为0-100之间的数字', 'warning')
                return render_template('order_manage/contract_new.html', order=order, params=params)
        if not is_number(request.form.get("material_loss_percent")):
            flash('耗损百分比必须为0-100之间的数字', 'warning')
            return render_template('order_manage/contract_new.html', order=order, params=params)
        if Decimal(request.form.get("material_loss_percent")) > Decimal("100") or Decimal(request.form.get("material_loss_percent")) < Decimal("0"):
            flash('耗损百分比必须为0-100之间的数字', 'warning')
            return render_template('order_manage/contract_new.html', order=order, params=params)
        contract_no = "SSCONTR%s" % datetime.datetime.now().strftime('%y%m%d%H%M%S')
        total_amount = Decimal("0")
        for order_content in order.order_contents:
            if not is_number(request.form.get("%sprice" % order_content.id)):
                flash('产品单价必须为数字', 'warning')
                return render_template('order_manage/contract_new.html', order=order, params=params)
            if not is_number(request.form.get("%samount" % order_content.id)):
                flash('产品总价必须为数字', 'warning')
                return render_template('order_manage/contract_new.html', order=order, params=params)
            total_amount += Decimal(request.form.get("%samount" % order_content.id))
            order_content.price = request.form.get("%sprice" % order_content.id)
            order_content.amount = request.form.get("%samount" % order_content.id)
            order_content.memo = request.form.get("%smemo" % order_content.id)
            db.session.add(order_content)
        contract_content = {"amount": request.form.get("amount"),
                            "delivery_time": request.form.get("delivery_time"),
                            "offer_no": 'YYS' + datetime.datetime.now().strftime('%y%m%d%H%M%S'),
                            "logistics_costs": request.form.get('logistics_costs'),
                            "live_floor_costs": request.form.get('live_floor_costs'),
                            "self_leveling_costs": request.form.get('self_leveling_costs'),
                            "crossed_line_costs": request.form.get('crossed_line_costs'),
                            "sticky_costs": request.form.get('sticky_costs'),
                            "full_adhesive_costs": request.form.get('full_adhesive_costs'),
                            "material_loss_percent": request.form.get('material_loss_percent'),
                            "material_loss": str(total_amount * Decimal(request.form.get("material_loss_percent")) /
                                                 Decimal("100")),
                            "other_costs": request.form.get('other_costs'),
                            "tax_costs": request.form.get('tax_costs'),
                            "tax_price": request.form.get('tax_price')}
        contract = Contract(
            contract_no=contract_no,
            order=order,
            contract_status="新合同",
            product_status="未生产",
            shipment_status="未出库",
            payment_status='未付款',
            contract_content=contract_content,
            user=order.user
        )
        order.order_status = '生成合同'
        db.session.add(contract)
        db.session.add(order)
        db.session.commit()
        product_name = ''
        for content in order.order_contents:
            "%s%s " % (product_name, content.product_name)
        WechatCall.send_template_to_user(str(order.user_id),
                                         "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0",
                                         {
                                             "first": {
                                                 "value": "您的订单状态已更改",
                                                 "color": "#173177"
                                             },
                                             "keyword1": {
                                                 "value": order.order_no,
                                                 "color": "#173177"
                                             },
                                             "keyword2": {
                                                 "value": order.order_status,
                                                 "color": "#173177"
                                             },
                                             "keyword3": {
                                                 "value": product_name,
                                                 "color": "#173177"
                                             },
                                             "remark": {
                                                 "value": "感谢您的使用！",
                                                 "color": "#173177"
                                             },
                                         },
                                         url_for('mobile_contract_show', id=contract.id)
                                         )
        cache.delete_memoized(current_user.get_orders_num)
        flash("合同生成成功", 'success')
        return redirect(url_for('order_manage.contract_index'))
    return render_template('order_manage/contract_new.html', order=order, params={})


@order_manage.route("/contracts/<int:id>/edit_contract", methods=['GET', 'POST'])
def contract_edit(id):
    contract = Contract.query.get_or_404(id)
    order = contract.order
    form = ContractForm(amount=contract.contract_content.get('amount'),
                        delivery_time=contract.contract_content.get('delivery_time'),
                        logistics_costs=contract.contract_content.get('logistics_costs'),
                        live_floor_costs=contract.contract_content.get('live_floor_costs'),
                        self_leveling_costs=contract.contract_content.get('self_leveling_costs'),
                        crossed_line_costs=contract.contract_content.get('crossed_line_costs'),
                        sticky_costs=contract.contract_content.get('sticky_costs'),
                        full_adhesive_costs=contract.contract_content.get('full_adhesive_costs'),
                        material_loss_percent=contract.contract_content.get('material_loss_percent'),
                        other_costs=contract.contract_content.get('other_costs'),
                        tax_costs=contract.contract_content.get('tax_costs'))
    if request.method == 'POST':
        if not is_number(request.form.get("amount")):
            flash('总金额必须为数字', 'warning')
            return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
        current_app.logger.info(request.form.get("delivery_time"))
        if request.form.get("delivery_time") is None or request.form.get("delivery_time") == '':
            flash('交货期必须填写', 'warning')
            return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
        if not request.form.get("tax_costs", '') == '':
            if not is_number(request.form.get("tax_costs")):
                flash('税点必须为0-100之间的数字', 'warning')
                return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
            if Decimal(request.form.get("tax_costs")) > Decimal("100") or Decimal(request.form.get("tax_costs")) < Decimal("0"):
                flash('税点必须为0-100之间的数字', 'warning')
                return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
        if not is_number(request.form.get("material_loss_percent")):
            flash('耗损百分比必须为0-100之间的数字', 'warning')
            return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
        if Decimal(request.form.get("material_loss_percent")) > Decimal("100") or Decimal(request.form.get("material_loss_percent")) < Decimal("0"):
            flash('耗损百分比必须为0-100之间的数字', 'warning')
            return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
        total_amount = Decimal("0")
        for order_content in order.order_contents:
            if not is_number(request.form.get("%sprice" % order_content.id)):
                flash('产品单价必须为数字', 'warning')
                return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
            if not is_number(request.form.get("%samount" % order_content.id)):
                flash('产品总价必须为数字', 'warning')
                return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
            total_amount += Decimal(request.form.get("%samount" % order_content.id))
            order_content.price = request.form.get("%sprice" % order_content.id)
            order_content.amount = request.form.get("%samount" % order_content.id)
            order_content.memo = request.form.get("%smemo" % order_content.id)
            db.session.add(order_content)
        contract_content = {"amount": request.form.get("amount"),
                            "delivery_time": request.form.get("delivery_time"),
                            "logistics_costs": request.form.get('logistics_costs'),
                            "live_floor_costs": request.form.get('live_floor_costs'),
                            "self_leveling_costs": request.form.get('self_leveling_costs'),
                            "crossed_line_costs": request.form.get('crossed_line_costs'),
                            "sticky_costs": request.form.get('sticky_costs'),
                            "full_adhesive_costs": request.form.get('full_adhesive_costs'),
                            "material_loss_percent": request.form.get('material_loss_percent'),
                            "material_loss": str(total_amount * Decimal(request.form.get("material_loss_percent")) /
                                                 Decimal("100")),
                            "other_costs": request.form.get('other_costs'),
                            "tax_costs": request.form.get('tax_costs'),
                            "tax_price": request.form.get('tax_price')}
        contract.contract_content = contract_content
        db.session.add(contract)
        db.session.add(order)
        db.session.commit()
        flash("合同修改成功", 'success')
        return redirect(url_for('order_manage.contract_index'))
    return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)


@order_manage.route("/orders/<int:id>/assign_sale_contact", methods=['GET', 'POST'])
def assign_sale_contact(id):
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        order.sale_contract = request.form.get('sale_contact')
        order.sale_contract_id = 1
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('order_manage.order_index'))
    return render_template('order_manage/assign_sale_contact.html', order=order)


@order_manage.route("/payment_status_update/<int:contract_id>", methods=['GET'])
def payment_status_update(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    contract.payment_status = '已付款'
    db.session.add(contract)
    db.session.commit()
    flash("付款状态修改成功", 'success')
    return redirect(url_for('order_manage.finance_contract_index'))


@order_manage.route("/contracts_index", methods=['GET'])
def contract_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    contracts = Contract.query.filter(
        Contract.user_id.in_(set([user.id for user in current_user.get_subordinate_dealers()]))).order_by(
        Contract.created_at.desc()).paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/contracts_index.html', contracts=contracts)


@order_manage.route("/finance_contracts_index", methods=['GET'])
def finance_contract_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    contracts = Contract.query.order_by(Contract.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/finance_contracts_index.html', contracts=contracts)


@order_manage.route("/contracts_for_tracking", methods=['GET'])
def contracts_for_tracking():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    contracts = Contract.query.filter_by(payment_status="已付款").order_by(Contract.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/contracts_for_tracking.html', contracts=contracts)


@order_manage.route("/contracts/<int:id>", methods=['GET'])
def contract_show(id):
    contract = Contract.query.get_or_404(id)
    return render_template('order_manage/contract_show.html', contract=contract)


@order_manage.route("/contract_offer/<int:id>", methods=['GET'])
def contract_offer(id):
    contract = Contract.query.get_or_404(id)
    return render_template('order_manage/contract_offer.html', contract=contract)


@order_manage.route('/tracking_infos')
def tracking_infos():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    tracking_infos = TrackingInfo.query.order_by(TrackingInfo.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/tracking_infos.html', tracking_infos=tracking_infos)


@order_manage.route('/tracking_info/new/<int:contract_id>', methods = ['GET', 'POST'])
def tracking_info_new(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    default_production_num = {}
    for order_content in contract.order.order_contents:
        default_production_num[order_content.sku_code] = order_content.number
        if not (order_content.batch_info == {} or order_content.batch_info is None):
            default_production_num[order_content.sku_code] = 0
        else:
            for inv in load_inventories_by_code(order_content.sku_code):
                for i in range(1, (len(inv.get("batches")) + 1)):
                    if int(inv.get("batches")[i - 1].get('stocks')) > order_content.number:
                        default_production_num[order_content.sku_code] = 0
    if not contract.shipment_status == '未出库':
        flash('不能重复生成物流状态', 'warning')
        return redirect(url_for('order_manage.contract_index'))
    if request.method == 'POST':
        form = TrackingInfoForm1(request.form)
        if form.validate():
            tracking_info = form.save(TrackingInfo(status='区域总监确认'))
            tracking_info.contract_no = contract.contract_no
            tracking_info.contract_date = contract.contract_date
            db.session.add(tracking_info)
            contract.shipment_status = '区域总监确认'
            db.session.add(contract)
            data_sku = []
            for order_content in contract.order.order_contents:
                if request.form.get('%s_production_num' % order_content.sku_code):
                    order_content.production_num = request.form.get('%s_production_num' % order_content.sku_code)
                inventory_choose = []
                batches = []
                sub_num = 0
                for inv in load_inventories_by_code(order_content.sku_code):
                    for i in range(1, (len(inv.get("batches")) + 1)):
                        if request.form.get('%s_%s_num' % (order_content.sku_code, inv.get("batches")[i-1].get('inv_id'))):
                            num = int(request.form.get('%s_%s_num' % (order_content.sku_code, inv.get("batches")[i-1].get('inv_id'))))
                            sub_num += num
                            inv_id = inv.get("batches")[i-1].get('inv_id')
                            inventory_choose.append({"username": inv.get('user_name'),
                                                     "batch_no": inv.get("batches")[i-1].get('batch_no'),
                                                     "production_date": inv.get("batches")[i-1].get('production_date'),
                                                     "inv_id": inv_id,
                                                     "num": num})
                            batches.append({"inv_id": inv_id, "sub_stocks": str(num)})
                data_sku.append({"code": order_content.sku_code, "stocks_for_order": str(-order_content.number), "batches": batches})
                order_content.inventory_choose = inventory_choose
                db.session.add(order_content)
            response = update_sku_by_code({"sku_infos": data_sku})
            if not response.status_code == 200:
                db.session.rollback()
                flash('物流状态创建失败', 'danger')
                return redirect(url_for('order_manage.tracking_info_new', contract_id=contract.id))
            db.session.commit()
            flash('物流状态创建成功', 'success')
            return redirect(url_for('order_manage.tracking_infos'))
        else:
            flash('对接人姓名和电话必须填写', 'danger')
            return redirect(url_for('order_manage.tracking_info_new', contract_id=contract.id))
    else:
        form = TrackingInfoForm1()
    return render_template('order_manage/tracking_info_new.html', contract=contract, form=form,
                           default_production_num=default_production_num)


@order_manage.route('/tracking_info/<int:id>/edit', methods=['GET', 'POST'])
def tracking_info_edit(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    contract = Contract.query.filter(Contract.contract_no == tracking_info.contract_no).first()
    delivery_infos_dict = {
        'tracking_no': '物流单号',
        'delivery_company': '货运公司名称',
        'delivery_tel': '货运公司电话',
        'goods_weight': '货物重量(kg)',
        'goods_count': '货物件数',
        'duration': '运输时间',
        'freight': '运费(元)',
        'pickup_no': '提货号码'
    }
    # 需默认值 recipient, recipient_phone, recipient_address
    today = datetime.datetime.now().strftime('%F')
    if request.method == 'POST':
        form = TrackingInfoForm2(request.form)
        tracking_info = form.save(tracking_info)
        tracking_info.delivery_infos = {
            'recipient': request.form.get('recipient'),
            'recipient_phone': request.form.get('recipient_phone'),
            'recipient_address': request.form.get('recipient_address'),
            'tracking_no': request.form.get('tracking_no'),
            'delivery_company': request.form.get('delivery_company'),
            'delivery_tel': request.form.get('delivery_tel'),
            'goods_weight': request.form.get('goods_weight'),
            'goods_count': request.form.get('goods_count'),
            'duration': request.form.get('duration'),
            'freight': request.form.get('freight'),
            'pickup_no': request.form.get('pickup_no')
        }
        db.session.add(tracking_info)
        db.session.commit()
        flash('物流状态更新成功', 'success')   
        return redirect(url_for('order_manage.tracking_infos'))  
    else:
        form = TrackingInfoForm2(obj=tracking_info)
    return render_template('order_manage/tracking_info_edit.html', tracking_info=tracking_info, form=form, today=today,
                           contract=contract, delivery_infos_dict=sorted(delivery_infos_dict.items()))


@order_manage.route('/tracking_info/<int:id>/generate_qrcode')
def tracking_info_generate_qrcode(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    if tracking_info.qrcode_image:
        return json.dumps({
            'status': 'error', 
            'message': 'qrcode already existed'
            })
    # qrcode token is a unique random string, generated by a specific rule
    # format looks like 'R>S8=@Zr{2[9zI/6@{CONTRACT_NO}', encoded by BASE64
    string = '%s@%s' % (gen_random_string(length=16), tracking_info.contract_no)
    qrcode_token = base64.b64encode(string.encode()).decode()
    filename = gen_qrcode(qrcode_token)
    if filename:
        tracking_info.qrcode_token = qrcode_token
        tracking_info.qrcode_image = filename
        tracking_info.save
    else:
        return json.dumps({
            'status': 'error',
            'message': 'generate qrcode failed'
            })
    return json.dumps({
        'status': 'success',
        'image_path': tracking_info.qrcode_image_path
        })

"""
@order_manage.route('/tracking_info/<int:id>/delete_qrcode')
def tracking_info_delete_qrcode(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    if tracking_info.qrcode_token and tracking_info.qrcode_image:
        qrcode_image_path = tracking_info.qrcode_image_path
        tracking_info.qrcode_token = None
        tracking_info.qrcode_image = None
        tracking_info.save
        delete_file(qrcode_image_path)
        flash('二维码删除成功', 'success')
    else:
        flash('操作失败', 'danger')
    return redirect(url_for('order_manage.tracking_info_edit', id=id))
"""

# download qrcode image
@order_manage.route('/tracking_info/<int:id>/qrcode')
def tracking_info_qrcode(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    response = make_response(send_file(app.config['STATIC_DIR'] + '/upload/qrcode/' + tracking_info.qrcode_image))
    response.headers['Content-Disposition'] = 'attachment; filename = %s' % tracking_info.qrcode_image
    return response


@order_manage.route('/region_profit')
def region_profit():
    provinces = []
    total_amount = []
    current_amount = []
    for area in SalesAreaHierarchy.query.filter_by(level_grade=3):

        user_ids = [user.id for user in db.session.query(User).join(User.sales_areas).filter(
            User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id == area.id)])).all()]
        contracts = Contract.query.filter_by(payment_status='已付款').filter(Contract.user_id.in_(user_ids)).all()
        amount = reduce(lambda x, y: x + y, [float(contract.contract_content.get('amount', '0'))
                                             for contract in contracts], 0)
        contract1s = Contract.query.filter_by(payment_status='已付款').filter(Contract.user_id.in_(user_ids)).filter(
                        Contract.created_at.between(datetime.datetime.utcnow() - datetime.timedelta(days=30),
                                                    datetime.datetime.utcnow())).all()
        amount1 = reduce(lambda x, y: x + y, [float(contract.contract_content.get('amount', '0'))
                                              for contract in contract1s], 0)
        provinces.append(str(area.name))
        total_amount.append(amount)
        current_amount.append(amount1)

    return render_template('order_manage/region_profit.html', provinces=provinces, total_amount=total_amount,
                           current_amount=current_amount)


@order_manage.route('/team_profit')
def team_profit():
    teams = []
    total_amount = []
    for region in SalesAreaHierarchy.query.filter_by(level_grade=2):
        us = db.session.query(User).join(User.departments).join(User.sales_areas).filter(
            User.user_or_origin == 3).filter(
            DepartmentHierarchy.name == "销售部").filter(
            SalesAreaHierarchy.id == region.id).first()
        if us is not None:
            teams.append(us.nickname)
            user_ids = [user.id for user in db.session.query(User).join(User.sales_areas).filter(
                User.user_or_origin == 2).filter(SalesAreaHierarchy.level_grade == 4).filter(
                SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                        SalesAreaHierarchy.parent_id == region.id)]))]))]
            contracts = Contract.query.filter_by(payment_status='已付款').filter(Contract.user_id.in_(user_ids)).all()
            amount = reduce(lambda x, y: x + y, [float(contract.contract_content.get('amount', '0'))
                                                 for contract in contracts], 0)

            total_amount.append(amount)
    return render_template('order_manage/team_profit.html', teams=teams, total_amount=total_amount)


@order_manage.route('/dealer_index')
def dealer_index():
    area = SalesAreaHierarchy.query.filter_by(name=request.args.get('province'), level_grade=3).first()
    datas = []
    if area is not None:
        for user in db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
                        SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                        SalesAreaHierarchy.parent_id == area.id)])).all():
            contracts = Contract.query.filter_by(user_id=user.id, payment_status='已付款').all()
            amount = reduce(lambda x, y: x + y, [float(contract.contract_content.get('amount', '0'))
                                                 for contract in contracts], 0)
            datas.append([user.nickname, amount])
        current_app.logger.info(datas)
    return render_template('order_manage/dealer_index.html', datas=datas)


@order_manage.route('/region_dealers')
def region_dealers():
    percentage = []
    regions = []
    datas = []
    day_datas = []
    months = [add_months(datetime.datetime.utcnow(), -4).strftime("%Y年%m月"),
              add_months(datetime.datetime.utcnow(), -3).strftime("%Y年%m月"),
              add_months(datetime.datetime.utcnow(), -2).strftime("%Y年%m月"),
              add_months(datetime.datetime.utcnow(), -1).strftime("%Y年%m月"),
              add_months(datetime.datetime.utcnow(), 0).strftime("%Y年%m月")]
    days = [
        (datetime.datetime.utcnow() + datetime.timedelta(days=-4)).strftime("%m月%d日"),
        (datetime.datetime.utcnow() + datetime.timedelta(days=-3)).strftime("%m月%d日"),
        (datetime.datetime.utcnow() + datetime.timedelta(days=-2)).strftime("%m月%d日"),
        (datetime.datetime.utcnow() + datetime.timedelta(days=-1)).strftime("%m月%d日"),
        (datetime.datetime.utcnow() + datetime.timedelta(days=0)).strftime("%m月%d日")
    ]
    for region in SalesAreaHierarchy.query.filter_by(level_grade=2):
        count = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).count()
        month1 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
                    User.created_at.between("2017-01-01", add_months(datetime.datetime.utcnow(), -4))).count()
        day1 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
            User.created_at.between("2017-01-01", datetime.datetime.utcnow() + datetime.timedelta(days=-4))).count()
        day2 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
            User.created_at.between("2017-01-01", datetime.datetime.utcnow() + datetime.timedelta(days=-3))).count()
        day3 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
            User.created_at.between("2017-01-01", datetime.datetime.utcnow() + datetime.timedelta(days=-2))).count()
        day4 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
            User.created_at.between("2017-01-01", datetime.datetime.utcnow() + datetime.timedelta(days=-1))).count()
        day5 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
            User.created_at.between("2017-01-01", datetime.datetime.utcnow() + datetime.timedelta(days=1))).count()
        month2 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
                    User.created_at.between("2017-01-01", add_months(datetime.datetime.utcnow(), -3))).count()
        month3 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
                    User.created_at.between("2017-01-01", add_months(datetime.datetime.utcnow(), -2))).count()
        month4 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
                    User.created_at.between("2017-01-01", add_months(datetime.datetime.utcnow(), -1))).count()
        month5 = db.session.query(User).join(User.sales_areas).filter(User.user_or_origin == 2).filter(
            SalesAreaHierarchy.level_grade == 4).filter(
            SalesAreaHierarchy.id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                SalesAreaHierarchy.parent_id.in_([area.id for area in SalesAreaHierarchy.query.filter(
                    SalesAreaHierarchy.parent_id == region.id)]))])).filter(
                    User.created_at.between("2017-01-01", datetime.datetime.utcnow() + datetime.timedelta(days=1))).count()
        regions.append(region.name)

        datas.append(
            {
                'name': region.name,
                'type': 'line',
                'data': [month1, month2, month3, month4, month5],
                'symbolSize': 5,
                'label': {
                    'normal': {
                        'show': 'false'
                    }
                },
                'smooth': 'false'
            }
        )
        day_datas.append(
            {
                'name': region.name,
                'type': 'line',
                'data': [day1, day2, day3, day4, day5],
                'symbolSize': 5,
                'label': {
                    'normal': {
                        'show': 'false'
                    }
                },
                'smooth': 'false'
            }
        )
        percentage.append({'value': count, 'name': region.name})
    return render_template('order_manage/region_dealers.html', percentage=percentage,
                           regions=regions, datas=datas, months=months, days=days, day_datas=day_datas)


@order_manage.route('/dealers_management/')
def dealers_management():
    form = UserSearchForm(request.args)
    form.reset_select_field()
    query = User.query.filter(User.user_or_origin == 2)
    if form.email.data:
        query = query.filter(User.email.contains(form.email.data))
    if form.nickname.data:
        query = query.filter(User.nickname.contains(form.nickname.data))
    if form.name.data:
        query = query.join(User.user_infos).filter(UserInfo.name.contains(form.name.data))
    if form.telephone.data:
        query = query.join(User.user_infos).filter(UserInfo.telephone.contains(form.telephone.data))
    if form.sale_range.data:
        query = query.join(User.sales_areas).filter(SalesAreaHierarchy.id == form.sale_range.data.id)
    users = query.order_by(User.created_at.desc())
    return object_list('order_manage/dealers_management.html', users, paginate_by=20, form=form)
