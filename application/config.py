# -*- coding: utf-8 -*-
import os


class Configuration(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or 'seesun'
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = set('jpg JPG png PNG gif GIF pdf PDF cad CAD rar RAR zip ZIP'.split())


class DevelopmentConfiguration(Configuration):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@127.0.0.1/seesun_crm'
    PRODUCT_SERVER = 'http://localhost:5001'
    WECHAT_TEST_MODE = True
    WECHAT_HOOK_URL = "http://118.178.185.40"


class TestConfiguration(Configuration):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun_db:UbqAI2017@121.43.175.216/seesun_crm_services_test_db'
    PRODUCT_SERVER = 'http://118.178.185.40:5000'
    WECHAT_TEST_MODE = True
    WECHAT_HOOK_URL = 'http://118.178.185.40'


class ProductionConfiguration(Configuration):
    SQLALCHEMY_DATABASE_URI = 'postgresql://seesun_db:UbqAI2017@121.43.175.216/seesun_crm_services_db'
    PRODUCT_SERVER = 'http://120.27.233.160:5000'
    WECHAT_TEST_MODE = True
    WECHAT_HOOK_URL = 'http://crm.seesun-pvcfloor.com'

config = {
    'default': DevelopmentConfiguration,
    'development': DevelopmentConfiguration,
    'test': TestConfiguration,
    'production': ProductionConfiguration
}
