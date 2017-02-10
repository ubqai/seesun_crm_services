# -*- coding: utf-8 -*-
import unittest
from unittest import TestCase
from flask import request
from main import app
import json

class AppTest(TestCase):
	def setUp(self):
		self.app = app.test_client()

	def test_homepage_works(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
	unittest.main()