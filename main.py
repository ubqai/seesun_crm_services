# -*- coding: utf-8 -*-
# This is a simple wrapper for running application
# $ python main.py
# $ gunicorn -w 4 -b 127.0.0.1:5000 main:app
import os
os.environ['FLASK_ENV'] = 'production'
from application import app
import application.views

if __name__ == '__main__':
    app.run()