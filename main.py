# -*- coding: utf-8 -*-
# This is a simple wrapper for running application
# $ python main.py
import os
os.environ['FLASK_ENV'] = 'production'
from application import app
import application.views

if __name__ == '__main__':
    app.run()