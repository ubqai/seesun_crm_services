from flask import Blueprint, flash, redirect, render_template, request, url_for
from .models import WebAccessLog
from ..helpers import object_list

web_access_log = Blueprint('web_access_log', __name__, template_folder='templates')


@web_access_log.route('/')
def root():
    return 'web access log homepage!'


@web_access_log.route('/index')
def index():
    query = WebAccessLog.query
    if request.args.get('platform'):
        query = query.filter(WebAccessLog.platform == request.args.get('platform'))
    if request.args.get('browser'):
        query = query.filter(WebAccessLog.browser == request.args.get('browser'))
    if request.args.get('created_at_gt'):
        query = query.filter(WebAccessLog.created_at >= request.args.get('created_at_gt'))
    if request.args.get('created_at_lt'):
        query = query.filter(WebAccessLog.created_at <= request.args.get('created_at_lt'))
    logs = query.order_by(WebAccessLog.created_at.desc())
    return object_list('web_access_log/index.html', logs, paginate_by=500)

