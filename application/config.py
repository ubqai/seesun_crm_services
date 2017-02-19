# -*- coding: utf-8 -*-
import os

class Configuration(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or 'seesun'
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = set('jpg JPG png PNG gif GIF'.split())

class DevelopmentConfiguration(Configuration):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'
    PRODUCT_SERVER = 'http://localhost:5001'

class TestConfiguration(Configuration):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'
    PRODUCT_SERVER = 'http://localhost:5001'

class ProductionConfiguration(Configuration):
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'
    PRODUCT_SERVER = 'http://localhost:5001'

config = {
    'default': DevelopmentConfiguration,
    'development': DevelopmentConfiguration,
    'test': TestConfiguration,
    'production': ProductionConfiguration
}