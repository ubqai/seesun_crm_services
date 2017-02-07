# -*- coding: utf-8 -*-
# extensions
from flask import Flask,g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate    import Migrate, MigrateCommand
from flask_script     import Manager

# internal models
from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)