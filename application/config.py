# -*- coding: utf-8 -*-
import os

class Configuration(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or 'seesun'
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = set('jpg JPG png PNG gif GIF pdf PDF'.split())

class DevelopmentConfiguration(Configuration):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'
    PRODUCT_SERVER = 'http://localhost:5001'
    WECHAT_TEST_MODE = True
    WECHAT_HOOK_URL = "http://118.178.185.40"

class TestConfiguration(Configuration):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'
    PRODUCT_SERVER = 'http://localhost:5001'
    WECHAT_TEST_MODE = True
    WECHAT_HOOK_URL = "http://118.178.185.40"

class ProductionConfiguration(Configuration):
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun_db:sEEsUn2o17@rm-bp1ksn1m18154025j.pg.rds.aliyuncs.com:3433/seesun_crm_services_db'
    PRODUCT_SERVER = 'http://118.178.185.40:5000'
    WECHAT_TEST_MODE = True
    WECHAT_HOOK_URL = "http://118.178.185.40"

config = {
    'default': DevelopmentConfiguration,
    'development': DevelopmentConfiguration,
    'test': TestConfiguration,
    'production': ProductionConfiguration
}