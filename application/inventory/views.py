# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template, url_for, request, flash, current_app
from ..models import *
from .api import load_categories, create_inventory, load_inventories, update_inventory, delete_inventory, load_inventory

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
        production_date = request.form.get('production_date')
        valid_until = request.form.get('valid_until')
        batch_no = request.form.get('batch_no')
        stocks = request.form.get('stocks')
        if user_id == '公司':
            inv_type = 1
            user_name = '公司'
            user_id = 0
        else:
            inv_type = 2
            user_name = User.query.get_or_404(user_id).nickname
        if stocks is None:
            flash('库存数量不能为空', 'danger')
            return render_template('inventory/new.html', id=id, users=User.query.filter_by(user_or_origin=2))
        elif int(stocks) < 1:
            flash('库存数量不能小于1', 'danger')
            return render_template('inventory/new.html', id=id, users=User.query.filter_by(user_or_origin=2))
        data = {'inventory_infos': [{"sku_id": id, "inventory": [{"type": inv_type, "user_id": user_id,
                                                                  "user_name": user_name,
                                                                  "production_date": production_date,
                                                                  "valid_until": valid_until,
                                                                  "batch_no": batch_no,
                                                                  "stocks": stocks}]}]}
        response = create_inventory(data)
        if response.status_code == 201:
            flash('库存创建成功', 'success')
        else:
            flash('库存创建失败', 'danger')
        return redirect(url_for('inventory.index'))
    return render_template('inventory/new.html', id=id, users=User.query.filter_by(user_or_origin=2))


@inventory.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    inventory = load_inventory(id)
    from_path = request.args.get('from')
    if request.method == 'POST':
        production_date = request.form.get('production_date')
        valid_until = request.form.get('valid_until')
        batch_no = request.form.get('batch_no')
        stocks = request.form.get('stocks')
        if stocks is None or stocks == '':
            flash('库存数量不能为空', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inventory)
        elif int(stocks) < 1:
            flash('库存数量不能小于1', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inventory)
        share_stocks = request.form.get('share_stocks')
        current_app.logger.info(share_stocks)
        if share_stocks is None or share_stocks == '':
            share_stocks = '0'
        if int(share_stocks) < 0:
            flash('共享库存数量不能小于0', 'danger')
            return render_template('inventory/edit.html', id=id, inventory=inventory)
        data = {"production_date": production_date, "valid_until": valid_until, "batch_no": batch_no,
                "stocks": str(int(stocks)), "share_stocks": str(int(share_stocks))}
        response = update_inventory(id, data)
        if response.status_code == 200:
            flash('库存修改成功', 'success')
        else:
            flash('库存修改失败', 'danger')
        if from_path == 'company':
            return redirect(url_for('inventory.index'))
        elif from_path == 'dealer':
            return redirect(url_for('inventory.share_index'))
    return render_template('inventory/edit.html', id=id, inventory=inventory, from_path=from_path)


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
