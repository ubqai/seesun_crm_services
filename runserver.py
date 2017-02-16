# -*- coding: utf-8 -*-
from application.app import app, db
import application.models
import application.views

if __name__ == '__main__':
	app.run()