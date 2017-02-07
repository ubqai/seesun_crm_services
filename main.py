# -*- coding: utf-8 -*-
from app import app, db
import models
import views

# blueprint config
from content.views import content
app.register_blueprint(content, url_prefix = '/content')

if __name__ == '__main__':
	app.run()