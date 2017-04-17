# -*- coding: utf-8 -*-
import os
from flask import Flask, g, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from .utils import num2moneyformat

from .config import config
from flask_cache import Cache

import logging

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV') or 'default'])
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "backstage_management.account_login"

bcrypt = Bcrypt(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

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
from .design_application.views import design_application

app.register_blueprint(design_application, url_prefix='/design_application')
from .project_report.views import project_report

app.register_blueprint(project_report, url_prefix='/project_report')
from .organization.views import organization

app.register_blueprint(organization, url_prefix='/organization')
from .web_access_log.views import web_access_log

app.register_blueprint(web_access_log, url_prefix='/web_access_log')

from .backstage_management.views import backstage_management

app.register_blueprint(backstage_management, url_prefix='/backstage_management')

from .inventory.api import load_products, load_skus, load_user_inventories, load_inventories_by_code

app.add_template_global(load_products)
app.add_template_global(load_skus)
app.add_template_global(load_user_inventories)
app.add_template_global(load_inventories_by_code)
app.add_template_global(len)
app.add_template_global(int)
app.add_template_global(str)
app.add_template_global(num2moneyformat)


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)
        app.logger.info("RUN ENV : [%s]" % os.getenv('FLASK_ENV'))


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
