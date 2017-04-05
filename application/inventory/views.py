# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template, url_for, request, flash, current_app
from ..models import *
from .api import load_categories, create_inventory, load_inventories, update_inventory, delete_inventory, load_inventory
from decimal import Decimal
from application.utils import is_number
from flask_login import current_user

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


@inventory.route('/share_inventory_list', methods=['GET'])
def share_inventory_list():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    sis = ShareInventory.query.filter(
        ShareInventory.applicant_id.in_(set([user.id for user in current_user.get_subordinate_dealers()]))).order_by(
        ShareInventory.created_at.desc()).paginate(page_index, per_page=page_size, error_out=True)
    return render_template('inventory/share_inventory_list.html', sis=sis)


@inventory.route('/audit_share_inventory/<int:id>', methods=['GET', 'POST'])
def audit_share_inventory(id):
    si = ShareInventory.query.get_or_404(id)
    if request.method == 'POST':
        status = request.form.get("status", '')
        price = request.form.get("price", '')
        params = {'status': status, 'price': price}
        if status == '':
            flash('状态必须选择', 'danger')
            return render_template('inventory/audit_share_inventory.html', si=si, params=params)
        if status == '审核通过':
            if price == '':
                flash('审核通过时，价格必须填写', 'danger')
                return render_template('inventory/audit_share_inventory.html', si=si, params=params)
            if not price == '':
                if not is_number(price):
                    flash('价格必须为数字', 'danger')
                    return render_template('inventory/audit_share_inventory.html', si=si, params=params)
                if Decimal(price) <= Decimal("0"):
                    flash('价格必须大于0', 'danger')
                    return render_template('inventory/audit_share_inventory.html', si=si, params=params)
        si.status = status
        if si.status == "审核通过":
            si.audit_price = price
            data = {'inventory_infos': [{"sku_id": si.sku_id, "inventory": [{"type": '2', "user_id": si.applicant_id,
                                                                             "user_name": si.app_user.nickname,
                                                                             "production_date": si.production_date,
                                                                             "batch_no": si.batch_no,
                                                                             "price": si.audit_price,
                                                                             "stocks": si.stocks}]}]}
            response = create_inventory(data)
            if not response.status_code == 201:
                flash('库存创建失败', 'danger')
                return render_template('inventory/audit_share_inventory.html', si=si, params={})
        db.session.add(si)
        db.session.commit()
        flash('工程剩余库存申请审核成功', 'success')
        return redirect(url_for('inventory.share_inventory_list'))
    return render_template('inventory/audit_share_inventory.html', si=si, params={})


@inventory.route('/show_share_inventory/<int:id>', methods=['GET'])
def show_share_inventory(id):
    si = ShareInventory.query.get_or_404(id)
    return render_template('inventory/show_share_inventory.html', si=si)
