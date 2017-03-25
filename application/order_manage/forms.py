# -*- coding: utf-8 -*-
from wtforms import Form, StringField, DateField
from wtforms.validators import *


class ContractForm(Form):
    amount = StringField('总金额', validators=[DataRequired(message='总金额必须输入')])
    delivery_time = StringField('交货期', validators=[DataRequired(message='交货期必须输入')])
    offer_no = StringField('要约NO.', validators=[DataRequired(message='要约NO必须输入')])
    logistics_costs = StringField('物流费用', validators=[DataRequired(message='物流费用必须输入')])
    live_floor_costs = StringField('活铺费用')
    self_leveling_costs = StringField('自流平费用')
    crossed_line_costs = StringField('划线费用')
    sticky_costs = StringField('点粘费用')
    full_adhesive_costs = StringField('全胶粘费用')
    material_loss_percent = StringField('耗损百分比', validators=[DataRequired(message='耗损百分比必须输入')])
    other_costs = StringField('其他费用')
    tax_costs = StringField('税点')


class TrackingInfoForm1(Form):
    contract_no = StringField('合同号', validators=[])
    contract_date = DateField('合同日期', validators=[])
    receiver_name = StringField('对接人姓名', validators=[DataRequired(message='对接人姓名必须填写')])
    receiver_tel = StringField('对接人电话', validators=[DataRequired(message='对接人电话必须填写')])

    def save(self, obj):
        self.populate_obj(obj)
        return obj


class TrackingInfoForm2(Form):
    production_date = DateField('生产日期', validators=[])
    production_manager = StringField('生产负责人', validators=[])
    production_starts_at = DateField('生产周期从', validators=[])
    production_ends_at = DateField('到', validators=[])
    delivery_date = DateField('配送日期', validators=[])
    #logistics_company = StringField('物流公司', validators=[])
    #delivery_man_name = StringField('司机姓名', validators=[])
    #delivery_man_tel = StringField('司机电话', validators=[])
    #delivery_plate_no = StringField('车牌号', validators=[])

    def save(self, obj):
        self.populate_obj(obj)
        return obj
