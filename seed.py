# -*- coding: utf-8 -*-
"""
$ python seed.py
Execute this file will create a bunch of sample data for mobile application display.
"""
from application.models import *

district = District(name="华东区", person_in_charge="马云").save
dealer = Dealer(name="马化腾", district=district).save

if not ContentCategory.query.filter(ContentCategory.name == '案例展示').first():
	cases = ContentCategory(name = '案例展示').save
	classification1 = ContentClassification(name = '按场景选择案例', description = '按场景选择案例', category_id = cases.id).save
	classification2 = ContentClassification(name = '按地域选择案例', description = '按地域选择案例', category_id = cases.id).save

	option_list_1 = ['校园专用', '医院专用', '球馆专用']
	option_list_2 = ['上海地区', '北京地区', '福建地区']
	for i in range(len(option_list_1)):
		option = ContentClassificationOption(name = option_list_1[i], classification_id = classification1.id).save
	for i in range(len(option_list_2)):
		option = ContentClassificationOption(name = option_list_2[i], classification_id = classification2.id).save

if not ContentCategory.query.filter(ContentCategory.name == '物料需要').first():
	wlxy = ContentCategory(name = '物料需要').save
	cls1 = ContentClassification(name = '物料下载', category_id = wlxy.id).save

	option_list = ['门头设计下载', '合同范本下载', '竞标范本下载', '日常设计下载', '促销内容下载', '促销设计下载']
	for name in option_list:
		option = ContentClassificationOption(name = name, classification_id = cls1.id).save

if not ContentCategory.query.filter(ContentCategory.name == '施工指导').first():
	sgzd = ContentCategory(name = '施工指导').save
	cls1 = ContentClassification(name = '施工内容及材料', category_id = sgzd.id).save

	option_list = ['自流平条件', '施工材料指导']
	for name in option_list:
		option = ContentClassificationOption(name = name, classification_id = cls1.id).save	






