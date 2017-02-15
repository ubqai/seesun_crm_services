"""
$ python seed.py
Execute this file will create a bunch of sample data for mobile application display.
"""
from models import *

option_list_1 = set(['运动系列产品', '商品系列产品', '家用休闲产品'])
option_list_2 = set(['校园专用', '医院专用', '球馆专用'])
option_list_3 = set(['上海地区', '北京地区', '福建地区'])
title_list    = set(['博格专版木纹', '博格木纹'])
content_list  = set(['无锡国家体育馆', '北京奥运会鸟巢'])
content_body = """
<div class="text">
<p>无锡国家体育馆</p>
<p>项目时间：2016/12/12</p>
<p>项目背景：聚氯乙烯100%新料</p>
<p>难度分析：未知</p>
<p>解决方案：未知</p>
</div>
<div class="divider3">&nbsp;</div>
<div class="text">
<p>现场拍摄</p>
<div class="text-img"><img class="full-img" src="/static/images/sport1.jpg" /></div>
<div class="text-img"><img class="full-img" src="/static/images/sport1.jpg" /></div>
<div class="text-img"><img class="full-img" src="/static/images/sport1.jpg" /></div>
</div>
"""

if not ContentCategory.query.filter(ContentCategory.name == '案例展示').first():
	category = ContentCategory(name = '案例展示').save
	classification1 = ContentClassification(name = '按产品选择案例', description = '按产品选择案例', category_id = category.id).save
	classification2 = ContentClassification(name = '按场景选择案例', description = '按场景选择案例', category_id = category.id).save
	classification3 = ContentClassification(name = '按地域选择案例', description = '按地域选择案例', category_id = category.id).save

	title1 = ContentTitle(name = '博格专版木纹', image_path = '/static/images/sport1.jpg').save
	title2 = ContentTitle(name = '博格木纹', image_path = '/static/images/sport2.jpg').save
	for name in content_list:
		Content(name = name, description = content_body, image_path = "/static/images/sport1.jpg", title_id = title1.id).save
		Content(name = name, description = content_body, image_path = "/static/images/sport1.jpg", title_id = title2.id).save

	for i in range(len(option_list_1)):
		option = ContentClassificationOption(name = option_list_1[i], classification_id = classification1.id).save
		title1.options.append(option)
		title1.save
		title2.options.append(option)
		title2.save
	for i in range(len(option_list_2)):
		option = ContentClassificationOption(name = option_list_2[i], classification_id = classification2.id).save
		title1.options.append(option)
		title1.save
		title2.options.append(option)
		title2.save
	for i in range(len(option_list_3)):
		option = ContentClassificationOption(name = option_list_3[i], classification_id = classification3.id).save
		title1.options.append(option)
		title1.save
		title2.options.append(option)
		title2.save



