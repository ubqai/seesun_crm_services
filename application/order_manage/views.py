# -*- coding: utf-8 -*-
import os
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

from .. import app, db
from ..models import *

order_manage = Blueprint('order_manage', __name__, template_folder='templates')


@order_manage.route("/orders")
def order_index():
    return render_template('order_manage/index.html')
