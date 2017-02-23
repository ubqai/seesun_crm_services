# -*- coding: utf-8 -*-
from wtforms import Form, StringField, DateField
from wtforms.validators import *


class ContractForm(Form):
    amount = StringField('总金额', validators=[DataRequired(message='总金额必须输入')])
    delivery_time = DateField('交货期', validators=[DataRequired(message='交货期必须输入')])
    offer_no = DateField('要约NO.', validators=[DataRequired(message='要约NO必须输入')])


