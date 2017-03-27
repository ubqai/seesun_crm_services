# -*- coding: utf-8 -*-
import json
from flask import Blueprint, flash, redirect, render_template, url_for, request, send_file, current_app
from flask.helpers import make_response
from .. import app
from ..models import *
from ..helpers import gen_qrcode, gen_random_string
from .forms import ContractForm, TrackingInfoForm1, TrackingInfoForm2
from ..inventory.api import load_inventories_by_code, update_sku_by_code
from application.utils import is_number
from decimal import Decimal

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
    if request.method == 'POST':
        if not is_number(request.form.get("amount")):
            flash('总金额必须为数字', 'warning')
            return render_template('order_manage/contract_new.html', form=form, order=order)
        current_app.logger.info(request.form.get("delivery_time"))
        if request.form.get("delivery_time") is None or request.form.get("delivery_time") == '':
            flash('交货期必须填写', 'warning')
            return render_template('order_manage/contract_new.html', form=form, order=order)
        if request.form.get("offer_no") is None or request.form.get("offer_no") == '':
            flash('要约NO.必须填写', 'warning')
            return render_template('order_manage/contract_new.html', form=form, order=order)
        if not is_number(request.form.get("logistics_costs")):
            flash('物流费用必须为数字', 'warning')
            return render_template('order_manage/contract_new.html', form=form, order=order)
        if not is_number(request.form.get("material_loss_percent")):
            flash('耗损百分比必须为0-100之间的数字', 'warning')
            return render_template('order_manage/contract_new.html', form=form, order=order)
        if Decimal(request.form.get("material_loss_percent")) > Decimal("100") or Decimal(request.form.get("material_loss_percent")) < Decimal("0"):
            flash('耗损百分比必须为0-100之间的数字', 'warning')
            return render_template('order_manage/contract_new.html', form=form, order=order)
        contract_no = "SSCONTR%s" % datetime.datetime.now().strftime('%y%m%d%H%M%S')
        total_amount = Decimal("0")
        for order_content in order.order_contents:
            if not is_number(request.form.get("%sprice" % order_content.id)):
                flash('产品单价必须为数字', 'warning')
                return render_template('order_manage/contract_new.html', form=form, order=order)
            if not is_number(request.form.get("%samount" % order_content.id)):
                flash('产品总价必须为数字', 'warning')
                return render_template('order_manage/contract_new.html', form=form, order=order)
            total_amount += Decimal(request.form.get("%samount" % order_content.id))
            order_content.price = request.form.get("%sprice" % order_content.id)
            order_content.amount = request.form.get("%samount" % order_content.id)
            order_content.memo = request.form.get("%smemo" % order_content.id)
            db.session.add(order_content)
        contract_content = {"amount": request.form.get("amount"),
                            "delivery_time": request.form.get("delivery_time"),
                            "offer_no": request.form.get("offer_no"),
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
                            "tax_costs": request.form.get('tax_costs')}
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
        return redirect(url_for('order_manage.contract_index'))
    return render_template('order_manage/contract_new.html', form=form, order=order)


@order_manage.route("/contracts/<int:id>/edit_contract", methods=['GET', 'POST'])
def contract_edit(id):
    contract = Contract.query.get_or_404(id)
    order = contract.order
    form = ContractForm(amount=contract.contract_content.get('amount'),
                        delivery_time=contract.contract_content.get('delivery_time'),
                        offer_no=contract.contract_content.get('offer_no'),
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
        if request.form.get("offer_no") is None or request.form.get("offer_no") == '':
            flash('要约NO.必须填写', 'warning')
            return render_template('order_manage/contract_edit.html', form=form, order=order, contract=contract)
        if not is_number(request.form.get("logistics_costs")):
            flash('物流费用必须为数字', 'warning')
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
                            "offer_no": request.form.get("offer_no"),
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
                            "tax_costs": request.form.get('tax_costs')}
        contract.contract_content = contract_content
        db.session.add(contract)
        db.session.add(order)
        db.session.commit()
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
    return redirect(url_for('order_manage.finance_contract_index'))


@order_manage.route("/contracts_index", methods=['GET'])
def contract_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    contracts = Contract.query.order_by(Contract.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/contracts_index.html', contracts=contracts)


@order_manage.route("/finance_contracts_index", methods=['GET'])
def finance_contract_index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    contracts = Contract.query.order_by(Contract.created_at.desc())\
        .paginate(page_index, per_page=page_size, error_out=True)
    return render_template('order_manage/finance_contracts_index.html', contracts=contracts)


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


@order_manage.route('/tracking_info/<int:id>/edit', methods=['GET', 'POST'])
def tracking_info_edit(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    contract = Contract.query.filter(Contract.contract_no == tracking_info.contract_no).first()
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
    if request.method == 'POST':
        form = TrackingInfoForm2(request.form)
        tracking_info = form.save(tracking_info)
        tracking_info.delivery_infos = {
            'recipient': request.form.get('recipient'),
            'tracking_no': request.form.get('tracking_no'),
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
    return render_template('order_manage/tracking_info_edit.html', tracking_info=tracking_info, form=form,
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
    # format looks like 'R>S8=@Zr{2[9zI/6@{CONTRACT_NO}'
    qrcode_token = '%s@%s' % (gen_random_string(length=16), tracking_info.contract_no)
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


# download qrcode image
@order_manage.route('/tracking_info/<int:id>/qrcode')
def tracking_info_qrcode(id):
    tracking_info = TrackingInfo.query.get_or_404(id)
    response = make_response(send_file(app.config['STATIC_DIR'] + '/upload/qrcode/' + tracking_info.qrcode_image))
    response.headers['Content-Disposition'] = 'attachment; filename = %s' % tracking_info.qrcode_image
    return response


@order_manage.route('/region_profit')
def region_profit():
    return render_template('order_manage/region_profit.html')


@order_manage.route('/team_profit')
def team_profit():
    return render_template('order_manage/team_profit.html')


@order_manage.route('/dealer_index')
def dealer_index():
    area = SalesAreaHierarchy.query.filter_by(name=request.args.get('province')).first()
    datas = []
    if area is not None:
        for sarea in SalesAreaHierarchy.query.filter_by(parent_id=area.id).all():
            for user in sarea.users.all():
                amount = float('0')
                for contract in Contract.query.filter_by(user_id=user.id, payment_status='已付款').all():
                    amount += float(contract.contract_content.get('amount', '0'))
                datas.append([user.nickname, amount])
        current_app.logger.info(datas)
    return render_template('order_manage/dealer_index.html', datas=datas)

