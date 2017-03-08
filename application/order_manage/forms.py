# -*- coding: utf-8 -*-
from wtforms import Form, StringField, DateField
from wtforms.validators import *


class ContractForm(Form):
    amount = StringField('总金额', validators=[DataRequired(message='总金额必须输入')])
    delivery_time = DateField('交货期', validators=[DataRequired(message='交货期必须输入')])
    offer_no = DateField('要约NO.', validators=[DataRequired(message='要约NO必须输入')])


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
    production_ends_at = DateField('到',validators=[])
    delivery_date = DateField('配送日期', validators=[])
    logistics_company = StringField('物流公司', validators=[])
    delivery_man_name = StringField('司机姓名', validators=[])
    delivery_man_tel = StringField('司机电话', validators=[])
    delivery_plate_no = StringField('车牌号', validators=[])

    def save(self, obj):
        self.populate_obj(obj)
        return obj