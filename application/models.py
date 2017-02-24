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
    image_links = db.Column(db.JSON, default=[])
    detail_link = db.Column(db.String(200))
    reference_info = db.Column(db.JSON, default={})
    product_ids = db.Column(db.JSON, default=[])
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    category_id = db.Column(db.Integer, db.ForeignKey('content_category.id'))
    options = db.relationship('ContentClassificationOption', secondary=contents_and_options,
                              backref=db.backref('contents', lazy='dynamic'), lazy='dynamic')

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

    contents = db.relationship('Content', backref='category', lazy='dynamic' )
    classifications = db.relationship('ContentClassification', backref='category', lazy='dynamic')

    def __repr__(self):
        return 'ContentCategory(id: %s, name: %s)' % (self.id, self.name)

    @property
    def delete_p(self):
        for classification in self.classifications:
            classification.delete_p
        self.delete
        return self

    @property
    def options(self):
        classification_ids = [classification.id for classification in self.classifications]
        options = ContentClassificationOption.query.filter(ContentClassificationOption.classification_id.in_(classification_ids))
        return options


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


class Material(db.Model, Rails):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    application_contents = db.relationship('MaterialApplicationContent', backref='material', lazy='dynamic')

    def __repr__(self):
        return 'Material(id: %s, name: %s, ...)' % (self.id, self.name)


class MaterialApplication(db.Model, Rails):
    id         = db.Column(db.Integer, primary_key=True)
    app_no     = db.Column(db.String(30), unique=True)
    status     = db.Column(db.String(50))
    memo       = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    application_contents = db.relationship('MaterialApplicationContent', backref='application', lazy='dynamic')

    def __repr__(self):
        return 'MaterialApplication(id: %s,...)' % (self.id)


class MaterialApplicationContent(db.Model, Rails):
    id          = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))
    number      = db.Column(db.Integer)
    created_at  = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at  = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    application_id = db.Column(db.Integer, db.ForeignKey('material_application.id'))

    def __repr__(self):
        return 'MaterialApplicationContent(id: %s, material_id: %s, number: %s,...)' % (self.id, self.material_id, self.number)


class Order(db.Model, Rails):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(30), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_status = db.Column(db.String(50))
    order_memo = db.Column(db.Text)
    buyer_info = db.Column(db.JSON)
    contracts = db.relationship('Contract', backref='order', lazy='dynamic')
    order_contents = db.relationship('OrderContent', backref='order')

    def __repr__(self):
        return 'Order(id: %s, order_no: %s, user_id: %s, order_status: %s, order_memo: %s)' % (
            self.id, self.order_no, self.user_id, self.order_status, self.order_memo)


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
    square_num = db.Column(db.Float)
    price = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)
    memo = db.Column(db.String(100))

    def __repr__(self):
        return 'OrderContent(id: %s, order_id: %s, product_name: %s, sku_specification: %s, sku_code: %s, number: %s, square_num: %s)' % (
            self.id, self.order_id, self.product_name, self.sku_specification, self.sku_code, self.number, self.square_num)


users_and_resources = db.Table(
    'users_and_resources',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('resource_id', db.Integer, db.ForeignKey('resources.id'))
)


users_and_sales_areas = db.Table(
    'users_and_sales_areas',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('sales_area_id', db.Integer, db.ForeignKey('sales_area_hierarchies.id'))
)


users_and_departments = db.Table(
    'users_and_departments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('dep_id', db.Integer, db.ForeignKey('department_hierarchies.id'))
)


class User(db.Model, Rails):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), nullable=False)
    nickname = db.Column(db.String(200))
    user_or_origin = db.Column(db.Integer)
    user_infos = db.relationship('UserInfo', backref='user')
    orders = db.relationship('Order', backref='user')
    material_applications = db.relationship('MaterialApplication', backref='user', lazy='dynamic')
    resources = db.relationship('Resource', secondary=users_and_resources,
                                backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    sales_areas = db.relationship('SalesAreaHierarchy', secondary=users_and_sales_areas,
                                  backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    departments = db.relationship('DepartmentHierarchy', secondary=users_and_departments,
                                  backref=db.backref('users', lazy='dynamic'), lazy='dynamic')


class UserInfo(db.Model):
    __tablename__ = 'user_infos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    telephone = db.Column(db.String(20))
    address = db.Column(db.String(500))
    title = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(400))


class SalesAreaHierarchy(db.Model):
    __tablename__ = 'sales_area_hierarchies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    parent_id = db.Column(db.Integer)
    level_grade = db.Column(db.Integer)


class DepartmentHierarchy(db.Model):
    __tablename__ = 'department_hierarchies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    parent_id = db.Column(db.Integer)
    level_grade = db.Column(db.Integer)




