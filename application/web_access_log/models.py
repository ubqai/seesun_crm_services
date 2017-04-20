import datetime
import re
from .. import db

# ----- request path classification -----
# Others
module0_paths = """
/mobile/index""".split()
# Product,
module1_paths = """
/mobile/product
/mobile/product/\d+""".split()
# Storage
module2_paths = """
/mobile/storage
/mobile/storage_show/\d+""".split()
# Share
module3_paths = """
/mobile/share
/mobile/share_index/\d+
/mobile/share_index_for_order/\d+
/mobile/share_storage_for_detail
/mobile/share_storage_for_region
/mobile/upload_share_index
/mobile/new_share_inventory/\d+""".split()
# Case
module4_paths = """
/mobile/case_show
/mobile/product_cases
/mobile/product_case/\d+
/mobile/case_classification/\d+
/mobile/case_content/\d+""".split()
# Project
module5_paths = """
/mobile/project_report/new
/mobile/project_report/index
/mobile/project_report/\d+""".split()
# Design
module6_paths = """
/mobile/design
/mobile/design_applications
/mobile/design_file/\d+""".split()
# Material
module7_paths = """
/mobile/material_need
/mobile/material_need_options/\d+
/mobile/material_need_contents/\d+
/mobile/material_application/new
/mobile/material_applications
/mobile/material_application/\d+
/mobile/material_application/\d+/reconfirm_accept
/mobile/material_application/\d+/cancel""".split()
# Order
module8_paths = """
/mobile/cart
/mobile/cart_delete/\d+
/mobile/create_order
/mobile/orders
/mobile/created_orders
/mobile/contract/\d+""".split()
# Tracking
module9_paths = """
/mobile/tracking
/mobile/tracking_info/\d+""".split()
# Verification
module10_paths = """
/wechat/mobile/verification
/wechat/mobile/user_binding
/wechat/server/authentication""".split()
# Guide
module11_paths = """
/mobile/construction_guide
/mobile/construction_guide_options/\d+
/mobile/construction_guide_contents/\d+""".split()
# After
module12_paths = """
/mobile/after_service""".split()

web_access_log_white_list = []
for seq in range(1, 13):
    if locals().get('module%d_paths' % seq):
        web_access_log_white_list += locals().get('module%d_paths' % seq)
web_access_log_white_list = set(web_access_log_white_list)


def can_take_record(request_path):
    for valid_path in web_access_log_white_list:
        regex = '\A%s\Z' % valid_path
        if re.match(regex, request_path):
            return True
    return False


class WebAccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_path = db.Column(db.String(200))
    user_id = db.Column(db.Integer)
    remote_addr = db.Column(db.String(15))
    user_agent = db.Column(db.String(500))
    platform = db.Column(db.String(20))
    browser = db.Column(db.String(20))
    version = db.Column(db.String(20))
    language = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return """
        WebAccessLog(id: {id}, request_path: {request_path}, user_id: {user_id}, remote_addr: {remote_addr},
        user_agent: {user_agent})
        """.format(id=self.id, request_path=self.request_path, user_id=self.user_id, remote_addr=self.remote_addr,
                   user_agent=self.user_agent)

    @classmethod
    def take_record(cls, request, current_user):
        return cls(request_path=request.path,
                   user_id=current_user.id,
                   remote_addr=request.access_route[0],
                   user_agent=request.user_agent.string,
                   platform=request.user_agent.platform,
                   browser=request.user_agent.browser,
                   version=request.user_agent.version,
                   language=request.user_agent.language)
