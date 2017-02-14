# -*- coding: utf-8 -*-
from app import app, db
import views
from content.views import content
app.register_blueprint(content, url_prefix = '/admin/content')

if __name__ == '__main__':
	app.run()