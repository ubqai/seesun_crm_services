# -*- coding: utf-8 -*-
import json
from flask import Blueprint, flash, redirect, render_template, url_for, request, send_file
from flask.helpers import make_response
from .. import app
from ..models import *
from ..helpers import gen_qrcode 
from .forms import ContractForm, TrackingInfoForm1, TrackingInfoForm2
from ..inventory.api import load_inventories_by_code, update_inventory, update_sku_by_code

order_manage = Blueprint('order_manage', __name__, template_folder='templates')


@order_manage.route("/orders", methods=['GET'])
def order_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    orders_page = Order.query.order_by(Order.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
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
    form = ContractForm()
    if request.method == 'POST':
        contract_no = "SSCONTR%s" % datetime.datetime.now().strftime('%y%m%d%H%M%S')
        contract_content = {"amount": request.form.get("amount"),
                            "delivery_time": request.form.get("delivery_time"),
                            "offer_no": request.form.get("offer_no"),
                            "sale_contract": request.form.get('sale_contract')}
        contract = Contract(
            contract_no=contract_no,
            order=order,
            contract_status="新合同",
            product_status="未生产",
            shipment_status="未出库",
            contract_content=contract_content,
            user=order.user
        )
        order.order_status = '生成合同'
        for order_content in order.order_contents:
            order_content.price = request.form.get("%sprice" % order_content.id)
            order_content.amount = request.form.get("%samount" % order_content.id)
            order_content.memo = request.form.get("%smemo" % order_content.id)
            db.session.add(order_content)
        db.session.add(contract)
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('order_manage.contract_index'))
    return render_template('order_manage/contract_new.html', form=form, order=order)


@order_manage.route("/contracts_index", methods=['GET'])
def contract_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    contracts = Contract.query.order_by(Contract.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/contracts_index.html', contracts=contracts)


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
            flash('物流状态创建失败', 'danger')
            return redirect(url_for('order_manage.tracking_info_new', contract_id = contract.id))
    else:
        form = TrackingInfoForm1()
    return render_template('order_manage/tracking_info_new.html', contract = contract, form = form)


@order_manage.route('/tracking_info/<int:id>/edit', methods = ['GET', 'POST'])
def tracking_info_edit(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    contract = Contract.query.filter(Contract.contract_no == tracking_info.contract_no).first()
    if request.method == 'POST':
        form = TrackingInfoForm2(request.form)
        tracking_info = form.save(tracking_info)
        db.session.add(tracking_info)
        db.session.commit()
        flash('物流状态更新成功', 'success')   
        return redirect(url_for('order_manage.tracking_infos'))  
    else:
        form = TrackingInfoForm2(obj = tracking_info)
    return render_template('order_manage/tracking_info_edit.html', tracking_info = tracking_info, form = form, contract = contract)


@order_manage.route('/tracking_info/<int:id>/generate_qrcode')
def tracking_info_generate_qrcode(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    if tracking_info.qrcode_image:
        return json.dumps({
            'status': 'error', 
            'message': 'qrcode already existed'
            })
    # qrcode token should be a unique random string, generated by a specific rule
    # use contract_no instead during developing step
    filename = gen_qrcode(tracking_info.contract_no)
    if filename:
        tracking_info.qrcode_token = tracking_info.contract_no
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


# download qrcode image
@order_manage.route('/tracking_info/<int:id>/qrcode')
def tracking_info_qrcode(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    response = make_response(send_file(app.config['STATIC_DIR'] + '/upload/qrcode/'  + tracking_info.qrcode_image))
    response.headers['Content-Disposition'] = 'attachment; filename = %s' % tracking_info.qrcode_image
    return response