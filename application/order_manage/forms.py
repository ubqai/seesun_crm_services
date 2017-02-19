# -*- coding: utf-8 -*-
from wtforms import Form, StringField, DateField
from wtforms.validators import *


class ContractForm(Form):
    amount = StringField('总金额', validators=[DataRequired(message='总金额必须输入')])
    delivery_time = DateField('交货时间', validators=[DataRequired(message='交货时间必须输入')])
    contract_date = DateField('合同日期', validators=[DataRequired(message='合同日期必须输入')])


