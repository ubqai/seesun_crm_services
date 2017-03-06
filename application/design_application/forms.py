# -*- coding: utf-8 -*-
from wtforms import Form, StringField, SelectField
from wtforms.validators import *

class DesignApplicationForm(Form):
	status = SelectField('申请状态', choices = [('新申请', '新申请'), ('申请通过', '申请通过'), ('申请不通过', '申请不通过')])