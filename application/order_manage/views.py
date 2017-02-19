# -*- coding: utf-8 -*-
import os
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

from .. import app, db
from ..models import *

order_manage = Blueprint('order_manage', __name__, template_folder='templates')


@order_manage.route("/orders")
def order_index():
    orders = Order.query.all()
    return render_template('order_manage/index.html', orders=orders)


@order_manage.route("/orders/<int:id>")
def order_show(id):
    order = Order.query.get_or_404(id)
    return render_template('order_manage/show.html', order=order)
