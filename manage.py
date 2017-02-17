# -*- coding: utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script  import Manager, Shell

from application import app, db
from application.models import *
import application.views

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

def make_shell_context():
	return dict(app = app, db = db, Content = Content, ContentCategory = ContentCategory, 
		ContentClassification = ContentClassification, ContentClassificationOption = ContentClassificationOption)
manager.add_command("shell", Shell(make_context = make_shell_context))

@manager.command
def test():
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity = 2).run(tests)

if __name__ == '__main__':
	manager.run()