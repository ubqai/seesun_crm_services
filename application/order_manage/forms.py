# -*- coding: utf-8 -*-
from wtforms import Form, StringField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import *
from ..models import SalesAreaHierarchy


class ContractForm(Form):
    amount = StringField('总金额', validators=[DataRequired(message='总金额必须输入')])
    delivery_time = StringField('交货期', validators=[DataRequired(message='交货期必须输入')])
    logistics_costs = StringField('物流费用', validators=[DataRequired(message='物流费用必须输入')])
    live_floor_costs = StringField('活铺费用')
    self_leveling_costs = StringField('自流平费用')
    crossed_line_costs = StringField('划线费用')
    sticky_costs = StringField('点粘费用')
    full_adhesive_costs = StringField('全胶粘费用')
    material_loss_percent = StringField('耗损百分比', validators=[DataRequired(message='耗损百分比必须输入')])
    other_costs = StringField('其他费用')
    tax_costs = StringField('税点')
    tax_price = StringField('税费')


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


    def save(self, obj):
        self.populate_obj(obj)
        return obj


class UserSearchForm(Form):
    email = StringField('邮箱')
    nickname = StringField('昵称')
    name = StringField('姓名')
    telephone = StringField('电话')
    sale_range_province = QuerySelectField(u'销售范围(省)', get_label="name", allow_blank=True)
    sale_range = QuerySelectField(u'销售范围', get_label="name", allow_blank=True)

    def reset_select_field(self):
        self.sale_range_province.query = get_dynamic_sale_range_query(3)
        self.sale_range.query = get_dynamic_sale_range_query(4)


def get_dynamic_sale_range_query(level_grade, parent_id=None):
    sas = SalesAreaHierarchy.query.filter(SalesAreaHierarchy.level_grade == level_grade)
    if parent_id is not None:
        sas = sas.filter_by(parent_id=parent_id)
    return sas.order_by(SalesAreaHierarchy.id).all()
