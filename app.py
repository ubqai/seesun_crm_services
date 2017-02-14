# -*- coding: utf-8 -*-
# extensions
import os
from flask import Flask,g
from flask_sqlalchemy import SQLAlchemy

# internal models
from config import config

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])
db = SQLAlchemy(app)