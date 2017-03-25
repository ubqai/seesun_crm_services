from flask import Blueprint, flash, redirect, render_template, request, url_for
from .models import *
from ..helpers import object_list

web_access_log = Blueprint('web_access_log', __name__, template_folder='templates')


@web_access_log.route('/')
def root():
    return 'web access log homepage!'


@web_access_log.route('/index')
def index():
    query = WebAccessLog.query
    query = filter_by_request_args(query)
    logs = query.order_by(WebAccessLog.created_at.desc())
    return object_list('web_access_log/index.html', logs, paginate_by=500,
                       platform_list=platform_list, browser_list=browser_list)


@web_access_log.route('/statistics')
def statistics():
    module_count_list = []
    for i in range(13):
        query = access_query(i)
        query = filter_by_request_args(query)
        module_count_list.append(query.count())
    platform_count_list = []
    for platform in platform_list:
        query = WebAccessLog.query
        query = filter_by_request_args(query)
        platform_count_list.append([platform, query.filter(WebAccessLog.platform == platform).count()])
    browser_count_list = []
    for browser in browser_list:
        query = WebAccessLog.query
        query = filter_by_request_args(query)
        browser_count_list.append([browser, query.filter(WebAccessLog.browser == browser).count()])
    return render_template('web_access_log/statistics.html', module_count_list=module_count_list,
                           platform_count_list=platform_count_list, browser_count_list=browser_count_list)


def access_query(module_no=None):
    if module_no in range(1, 13):
        if module_no == 1:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.ilike('/mobile/product') |
                WebAccessLog.request_path.ilike('/mobile/product/%'))
        elif module_no == 2:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.ilike('/mobile/storage') |
                WebAccessLog.request_path.ilike('/mobile/storage_show/%'))
        elif module_no == 3:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.ilike('/mobile/share') |
                WebAccessLog.request_path.ilike('/mobile/share_index/%') |
                WebAccessLog.request_path.ilike('/mobile/share_storage_for_detail') |
                WebAccessLog.request_path.ilike('/mobile/upload_share_index') |
                WebAccessLog.request_path.ilike('/mobile/new_share_inventory/%'))
        elif module_no == 4:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.ilike('/mobile/case_show') |
                WebAccessLog.request_path.ilike('/mobile/product_cases') |
                WebAccessLog.request_path.ilike('/mobile/product_case/%') |
                WebAccessLog.request_path.ilike('/mobile/case_classification/%') |
                WebAccessLog.request_path.ilike('/mobile/case_content/%'))
        elif module_no == 5:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/project_report'))
        elif module_no == 6:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/design'))
        elif module_no == 7:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/material'))
        elif module_no == 8:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.ilike('/mobile/cart') |
                WebAccessLog.request_path.ilike('/mobile/cart_delete/%') |
                WebAccessLog.request_path.ilike('/mobile/create_order') |
                WebAccessLog.request_path.ilike('/mobile/orders') |
                WebAccessLog.request_path.ilike('/mobile/created_orders') |
                WebAccessLog.request_path.ilike('/mobile/contract/%'))
        elif module_no == 9:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/tracking'))
        elif module_no == 10:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/wechat/'))
        elif module_no == 11:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/construction_guide'))
        elif module_no == 12:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/after_service'))
    return WebAccessLog.query


def filter_by_request_args(query):
    if request.args.get('platform'):
        query = query.filter(WebAccessLog.platform == request.args.get('platform'))
    if request.args.get('browser'):
        query = query.filter(WebAccessLog.browser == request.args.get('browser'))
    if request.args.get('created_at_gt'):
        query = query.filter(WebAccessLog.created_at >= request.args.get('created_at_gt'))
    if request.args.get('created_at_lt'):
        query = query.filter(WebAccessLog.created_at <= request.args.get('created_at_lt'))
    return query

platform_list = sorted('aix amiga android bsd chromeos hpux iphone ipad irix linux macos sco solaris wii'
                       ' windows'.split())
browser_list = sorted('aol ask camino chrome firefox galeon google kmeleon konqueror links lynx msie msn netscape '
                      'opera safari seamonkey webkit yahoo'.split())


