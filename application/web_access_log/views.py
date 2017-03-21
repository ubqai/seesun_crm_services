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


@web_access_log.route('/statistics')
def statistics():
    count_list = [access_count(i) for i in range(0, 13)]
    return render_template('web_access_log/statistics.html', count_list=count_list)


def access_count(module_no=None):
    if module_no in range(13):
        if module_no == 0:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/index')).count()
        elif module_no == 1:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/product')).count()
        elif module_no == 2:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/storage')).count()
        elif module_no == 3:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.startswith('/mobile/share') |
                WebAccessLog.request_path.startswith('/mobile/upload_share_index') |
                WebAccessLog.request_path.startswith('/mobile/new_share_inventory/')).count()
        elif module_no == 4:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.startswith('/mobile/case') |
                WebAccessLog.request_path.startswith('/mobile/product_case')).count()
        elif module_no == 5:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/project_report')).count()
        elif module_no == 6:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/design')).count()
        elif module_no == 7:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/material')).count()
        elif module_no == 8:
            return WebAccessLog.query.filter(
                WebAccessLog.request_path.startswith('/mobile/cart') |
                WebAccessLog.request_path.startswith('/mobile/create_order') |
                WebAccessLog.request_path.startswith('/mobile/orders') |
                WebAccessLog.request_path.startswith('/mobile/created_orders') |
                WebAccessLog.request_path.startswith('/mobile/contract/')).count()
        elif module_no == 9:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/tracking')).count()
        elif module_no == 10:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/wechat/')).count()
        elif module_no == 11:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/construction_guide')).count()
        elif module_no == 12:
            return WebAccessLog.query.filter(WebAccessLog.request_path.startswith('/mobile/after_service')).count()
    return WebAccessLog.query.count()

"""
# ----- request path classification -----
# Module 0 Other
other_path_list = ['/mobile/index']
# Module 1 Product
product_path_list = ['/mobile/product']
# Module 2 Storage
storage_path_list = ['/mobile/storage']
# Module 3 Share
share_path_list = ['/mobile/share', '/mobile/upload_share_index', '/mobile/new_share_inventory/']
# Module 4 Case
case_path_list = ['/mobile/case', '/mobile/product_case']
# Module 5 Project
project_path_list = ['/mobile/project_report/']
# Module 6 Design
design_path_list = ['/mobile/design']
# Module 7 Material
material_path_list = ['/mobile/material']
# Module 8 Order
order_path_list = ['/mobile/cart', '/mobile/create_order', '/mobile/orders', '/mobile/created_orders',
                   '/mobile/contract/']
# Module 9 Tracking
tracking_path_list = ['/mobile/tracking']
# Module 10 Verification
verification_path_list = ['/wechat/']
# Module 11 Guide
guide_path_list = ['/mobile/construction_guide']
# Module 12 After
after_path_list = ['/mobile/after_service']
"""
