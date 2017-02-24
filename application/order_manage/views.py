# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template, url_for, request
from ..models import *
from .forms import ContractForm

order_manage = Blueprint('order_manage', __name__, template_folder='templates')


@order_manage.route("/orders", methods=['GET'])
def order_index():
    orders = Order.query.all()
    return render_template('order_manage/index.html', orders=orders)


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
            contract_content=contract_content
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
    contracts = Contract.query.all()
    return render_template('order_manage/contracts_index.html', contracts=contracts)


@order_manage.route("/contracts/<int:id>", methods=['GET'])
def contract_show(id):
    contract = Contract.query.get_or_404(id)
    return render_template('order_manage/contract_show.html', contract=contract)


@order_manage.route("/contract_offer/<int:id>", methods=['GET'])
def contract_offer(id):
    contract = Contract.query.get_or_404(id)
    return render_template('order_manage/contract_offer.html', contract=contract)
