# -*- coding: utf-8 -*-
import os
from flask import Flask, g, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from .config import config

import logging

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV') or 'default'])
db = SQLAlchemy(app)

from .content.views import content
app.register_blueprint(content, url_prefix='/content')
from .product.views import product
app.register_blueprint(product, url_prefix='/product')
from .order_manage.views import order_manage
app.register_blueprint(order_manage, url_prefix='/order_manage')
from .inventory.views import inventory
app.register_blueprint(inventory, url_prefix='/inventory')
from .wechat.views import wechat
app.register_blueprint(wechat, url_prefix='/wechat')

from .inventory.api import load_products, load_skus
app.add_template_global(load_products)
app.add_template_global(load_skus)
app.add_template_global(len)

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/')
def root():
    return redirect(url_for('mobile_index'))

@app.route('/admin')
def admin():
    return redirect(url_for('content.category_index'))