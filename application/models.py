# -*- coding: utf-8 -*-
import datetime
from . import db


class Rails(object):
    @property
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @property
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


# Contents_and_options: id, content_id, content_classification_option_id
contents_and_options = db.Table('contents_and_options',
                                db.Column('content_id', db.Integer, db.ForeignKey('content.id')),
                                db.Column('content_classification_option_id', db.Integer,
                                          db.ForeignKey('content_classification_option.id'))
    )


# Contents: id, name,description,content_thumbnail,reference_info(json{name,value})
class Content(db.Model, Rails):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    reference_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    options = db.relationship('ContentClassificationOption', secondary=contents_and_options,
                              backref=db.backref('contents', lazy='dynamic'))

    def __repr__(self):
        return 'Content(id: %s, name: %s, ...)' % (self.id, self.name)

    def append_options(self, options):
        existing_options = self.options
        new_options = []
        for option in options:
            if option not in existing_options:
                new_options.append(option)
        for option in new_options:
            existing_options.append(option)
        return self.options

    def update_options(self, options):
        self.options = []
        self.append_options(options)
        return self.options


# Content_categories: id,name
class ContentCategory(db.Model, Rails):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    classifications = db.relationship('ContentClassification', backref='category', lazy='dynamic')

    def __repr__(self):
        return 'ContentCategory(id: %s, name: %s)' % (self.id, self.name)

    @property
    def delete_p(self):
        for classification in self.classifications:
            classification.delete_p
        self.delete
        return self


# Content_classifications: id, content_category_id, name,description
class ContentClassification(db.Model, Rails):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    category_id = db.Column(db.Integer, db.ForeignKey('content_category.id'))
    options = db.relationship('ContentClassificationOption', backref='classification', lazy='dynamic')

    def __repr__(self):
        return 'ContentClassification(id: %s, name: %s, description: %s)' % (self.id, self.name, self.description)

    @property
    def delete_p(self):
        for option in self.options:
            option.delete
        self.delete
        return self


# Content_classification_options: id, content_classification_id,name
class ContentClassificationOption(db.Model, Rails):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    classification_id = db.Column(db.Integer, db.ForeignKey('content_classification.id'))

    def __repr__(self):
        return 'ContentClassificationOption(id: %s, name: %s)' % (self.id, self.name)


class District(db.Model, Rails):
    __tablename__ = 'districts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    person_in_charge = db.Column(db.String(200))
    dealers = db.relationship('Dealer', backref='district')

    def __repr__(self):
        return 'District(id: %s, name: %s, person_in_charge: %s)' % (self.id, self.name, self.person_in_charge)


class Dealer(db.Model, Rails):
    __tablename__ = 'dealers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    orders = db.relationship('Order', backref='dealer')

    def __repr__(self):
        return 'Dealer(id: %s, name: %s, district_id: %s)' % (self.id, self.name, self.district_id)


class Order(db.Model, Rails):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(30), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.id'))
    order_status = db.Column(db.String(50))
    order_memo = db.Column(db.Text)
    contracts = db.relationship('Contract', backref='order', lazy='dynamic')
    order_contents = db.relationship('OrderContent', backref='order')

    def __repr__(self):
        return 'Order(id: %s, order_no: %s, dealer_id: %s, order_status: %s, order_memo: %s)' % (
            self.id, self.order_no, self.dealer_id, self.order_status, self.order_memo)


class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(30), unique=True)
    contract_date = db.Column(db.DateTime, default=datetime.datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    contract_status = db.Column(db.String(50))
    product_status = db.Column(db.String(50))
    shipment_status = db.Column(db.String(50))
    contract_content = db.Column(db.JSON)

    def __repr__(self):
        return 'Contract(id: %s, contract_no: %s, contract_date: %s, order_id: %s, contract_status: %s, product_status: %s, shipment_status: %s, ...)' % (
            self.id, self.contract_no, self.contract_date, self.order_id, self.contract_status, self.product_status, self.shipment_status)


class OrderContent(db.Model, Rails):
    __tablename__ = 'order_contents'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_name = db.Column(db.String(300))
    sku_specification = db.Column(db.String(500))
    sku_code = db.Column(db.String(30))
    number = db.Column(db.Integer)
    square_num = db.Column(db.Integer)

    def __repr__(self):
        return 'OrderContent(id: %s, order_id: %s, product_name: %s, sku_specification: %s, sku_code: %s, number: %s, square_num: %s)' % (
            self.id, self.order_id, self.product_name, self.sku_specification, self.sku_code, self.number, self.square_num)