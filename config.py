# -*- coding: utf-8 -*-
import os
class Configuration(object):
	DEBUG = True
	SECRET_KEY = 'seesun'

	APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
	STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
	IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
	# database
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_DATABASE_URI = 'postgresql://seesun:123456@localhost/seesun_crm'