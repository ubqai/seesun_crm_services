# -*- coding: utf-8 -*-
import os
class Configuration(object):
	SECRET_KEY = os.getenv('SECRET_KEY') or 'seesun'
	APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
	STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
	IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
	# database
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	# file uploading
	MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfiguration(Configuration):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'

class TestConfiguration(Configuration):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'

class ProductionConfiguration(Configuration):
	SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'

config = {
	'default': DevelopmentConfiguration,
	'development': DevelopmentConfiguration,
	'test': TestConfiguration,
	'production': ProductionConfiguration
}