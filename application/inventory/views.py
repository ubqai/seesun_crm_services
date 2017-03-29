# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template, url_for, request, flash, current_app
from ..models import *
from .api import load_categories, create_inventory, load_inventories, update_inventory, delete_inventory, load_inventory
from decimal import Decimal
from application.utils import is_number

inventory = Blueprint('inventory', __name__, template_folder='templates')


@inventory.route('/', methods=['GET'])
def index():
    categories = load_categories()
    return render_template('inventory/index.html', categories=categories)


@inventory.route('/sku/<int:id>', methods=['GET'])
def list_invs(id):
    invs = load_inventories(id)
    return render_template('inventory/list_invs.html', invs=invs)


@inventory.route('/new/<int:id>', methods=['GET', 'POST'])
def new(id):
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        inv_type = request.form.get('inv_type')
        production_date = request.form.get('production_date', '')
        batch_no = 'BT%s%s' % (datetime.datetime.now().strftime('%y%m%d%H%M%S'), inv_type)
        stocks = request.form.get('stocks', '')
        price = request.form.get('price', '')
        user_name = '公司'
        params = {'user_id': user_id, 'inv_type': inv_type, 'production_date': production_date,
                  'stocks': stocks, "price": price}
        current_app.logger.info(params)
        if production_date == '':
            flash('生产日期不能为空', 'danger')
            return render_template('inventory/new.html', id=id, params=params)
        if stocks == '':
            flash('库存数量不能为空', 'danger')
            return render_template('inventory/new.html', id=id, params=params)
        if not is_number(stocks):
            flash('库存数量必须为数字', 'danger')
            return render_template('inventory/new.html', id=id, params=params)
        if Decimal(stocks) <= Decimal("0"):
            flash('库存数量必须大于0', 'danger')
            return render_template('inventory/new.html', id=id, params=params)
        if inv_type == '2' and price == '':
            flash('尾货库存价格必须填写', 'danger')
            return render_template('inventory/new.html', id=id, params=params)
        if not price == '':
            if not is_number(price):
                flash('价格必须为数字', 'danger')
                return render_template('inventory/new.html', id=id, params=params)
            if Decimal(price) <= Decimal("0"):
                flash('价格必须大于0', 'danger')
                return render_template('inventory/new.html', id=id, params=params)
        data = {'inventory_infos': [{"sku_id": id, "inventory": [{"type": inv_type, "user_id": user_id,
                                                                  "user_name": user_name,
                                                                  "production_date": production_date,
                                                                  "batch_no": batch_no,
                                                                  "price": price,
                                                                  "stocks": stocks}]}]}
        response = create_inventory(data)
        if response.status_code == 201:
            flash('库存创建成功', 'success')
        else:
            flash('库存创建失败', 'danger')
        return redirect(url_for('inventory.index'))
    return render_template('inventory/new.html', id=id, params={})


@inventory.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    inv = load_inventory(id)
    from_path = request.args.get('from')
    if request.method == 'POST':
        production_date = request.form.get('production_date', '')
        stocks = request.form.get('stocks', '')
        price = request.form.get('price', '')
        if production_date == '':
            flash('生产日期不能为空', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inv)
        if stocks == '':
            flash('库存数量不能为空', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inv)
        if not is_number(stocks):
            flash('库存数量必须为数字', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inv)
        if Decimal(stocks) <= Decimal("0"):
            flash('库存数量必须大于0', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inv)
        if inv.get('type') == 2 and price == '':
            flash('尾货库存价格必须填写', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inv)
        if not price == '':
            if not is_number(price):
                flash('价格必须为数字', 'danger')
                return render_template('inventory/edit.html', id=id, inventory=inv)
            if Decimal(price) <= Decimal("0"):
                flash('价格必须大于0', 'danger')
                return render_template('inventory/edit.html', id=id, inventory=inv)
        data = {"production_date": production_date, "stocks": str(Decimal(stocks)), "price": price}
        response = update_inventory(id, data)
        if response.status_code == 200:
            flash('库存修改成功', 'success')
        else:
            flash('库存修改失败', 'danger')
        if from_path == 'company':
            return redirect(url_for('inventory.index'))
        elif from_path == 'dealer':
            return redirect(url_for('inventory.share_index'))
    return render_template('inventory/edit.html', id=id, inventory=inv, from_path=from_path)


@inventory.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if request.method == 'POST':
        response = delete_inventory(id)
        if response.status_code == 200:
            flash('库存批次删除成功', 'success')
        else:
            flash('库存批次删除失败', 'danger')
    return redirect(url_for('inventory.index'))


@inventory.route('/share_index', methods=['GET'])
def share_index():
    categories = load_categories()
    user_id = User.query.filter_by(user_or_origin=2, nickname='普陀区经销商').first().id
    return render_template('inventory/share_index.html', categories=categories, user_id=user_id)
