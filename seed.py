# -*- coding: utf-8 -*-
"""
$ python seed.py
Execute this file will create a bunch of sample data for mobile application display.
"""
from application.models import *

if not SalesAreaHierarchy.query.filter_by(name='上海市').first():
    sa = SalesAreaHierarchy(name='上海市')
    db.session.add(sa)
    db.session.commit()

sales_area = SalesAreaHierarchy.query.filter_by(name='上海市').first()
if not User.query.filter(User.email == 'abc@hotmail.con').first():
    user1 = User(email='abc@hotmail.con', nickname='普陀区经销商', user_or_origin=2,
                 password_hash='$2b$12$4FCkZd8nJohWa7MfqrHmIec7JVYe/oiHOR4q.8.dYWnN3ahdQViF2')
    user1.sales_areas.append(sales_area)
    user1.save
if not User.query.filter(User.email == 'bcd@hotmail.con').first():
    user2 = User(email='bcd@hotmail.con', nickname='长宁区经销商', user_or_origin=2,
                 password_hash='$2b$12$4FCkZd8nJohWa7MfqrHmIec7JVYe/oiHOR4q.8.dYWnN3ahdQViF2')
    user2.sales_areas.append(sales_area)
    user2.save

if not ContentCategory.query.filter(ContentCategory.name == '案例展示').first():
    cases = ContentCategory(name='案例展示').save
    classification1 = ContentClassification(name='按场景选择案例', description='按场景选择案例', category_id=cases.id).save
    classification2 = ContentClassification(name='按地域选择案例', description='按地域选择案例', category_id=cases.id).save

    option_list_1 = ['校园专用', '医院专用', '球馆专用']
    option_list_2 = ['上海地区', '北京地区', '福建地区']
    for i in range(len(option_list_1)):
        option = ContentClassificationOption(name=option_list_1[i], classification_id=classification1.id).save
    for i in range(len(option_list_2)):
        option = ContentClassificationOption(name=option_list_2[i], classification_id=classification2.id).save

if not ContentCategory.query.filter(ContentCategory.name == '物料需要').first():
    wlxy = ContentCategory(name='物料需要').save
    cls1 = ContentClassification(name='物料下载', category_id=wlxy.id).save

    option_list = ['门头设计下载', '合同范本下载', '竞标范本下载', '日常设计下载', '促销内容下载', '促销设计下载']
    for name in option_list:
        option = ContentClassificationOption(name=name, classification_id=cls1.id).save

if not ContentCategory.query.filter(ContentCategory.name == '施工指导').first():
    sgzd = ContentCategory(name='施工指导').save
    cls1 = ContentClassification(name='施工内容及材料', category_id=sgzd.id).save

    option_list = ['自流平条件', '施工材料指导']
    for name in option_list:
        option = ContentClassificationOption(name=name, classification_id=cls1.id).save

material_list = '运动展柜 商用展柜 家用展柜 博格画册 专版画册 锐动系列 帝彩尚丽 帝彩尚高 认证证书'.split()
for i in material_list:
    if not Material.query.filter(Material.name == i).first():
        Material(name=i).save

dh_array = '董事长 销售部 仓储物流部 电商部 设计部 市场部 售后部'.split()
for dh_name in dh_array:
    if not DepartmentHierarchy.query.filter_by(name=dh_name).first():
        dh = DepartmentHierarchy(name=dh_name)
        if dh_name == "董事长":
            dh.level_grade = 1
        else:
            dh.level_grade = 2
            dh.parent_id = DepartmentHierarchy().query.filter_by(name='董事长').first().id
        db.session.add(dh)
        db.session.commit()

if not User.query.filter_by(email="admin@hotmail.com").first():
    u = User(email="admin@hotmail.com", nickname="admin", user_or_origin=3, password='1qaz@WSX')
    dh = DepartmentHierarchy().query.filter_by(level_grade=1).first()
    u.departments.append(dh)
    u.save

webpage_describe_list = [
    ("order_manage.dealer_index", "GET", "各省经销商销售统计"),
    ("order_manage.region_profit", "GET", "各省销售统计"),
    ("order_manage.order_index", "GET", "订单列表"),
    ("order_manage.contract_index", "GET", "合同列表"),
    ("content.material_application_index", "GET", "物料申请"),
    ("project_report.index", "GET", "项目报备申请"),
    ("inventory.share_inventory_list", "GET", "工程剩余库存申请审核"),
    ("order_manage.finance_contract_index", "GET", "合同列表"),
    ("product.category_index", "GET", "产品"),
    ("inventory.index", "GET", "库存"),
    ("design_application.index", "GET", "待设计列表"),
    ("content.category_index", "GET", "内容"),
    ("order_manage.contracts_for_tracking", "GET", "生产合同列表"),
    ("order_manage.tracking_infos", "GET", "物流状态列表"),
    ("web_access_log.statistics", "GET", "点击率统计"),
    ("order_manage.team_profit", "GET", "销售团队销售统计"),
    ("organization.user_index", "GET", "用户管理"),
    ("organization.authority_index", "GET", "组织架构及权限组"),
    ("organization.regional_and_team_index", "GET", "区域管理和销售团队"),
]

dh = DepartmentHierarchy.query.filter_by(name="董事长").first()
for (endpoint, method, describe) in webpage_describe_list:
    wd = WebpageDescribe(endpoint=endpoint, method=method, describe=describe)
    if endpoint == "organization.user_index":
        wd.validate_flag = False
    wd.check_data()
    wd.save
    AuthorityOperation(webpage_id=wd.id, role_id=dh.id, flag="Y").save


wd = WebpageDescribe.query.filter_by(endpoint="organization.user_index").first()
if wd:
    wd.validate_flag = True
    wd.save