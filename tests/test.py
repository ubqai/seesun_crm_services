# -*- coding: utf-8 -*-
import unittest
from flask import request
from app import app
import json

class HttpTest(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()

	def test_get_root_redirect(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 302)

	def test_get_mobile_index(self):
		response = self.app.get('/mobile_index')
		self.assertEqual(response.status_code, 200)

	def test_get_admin_redirect(self):
		response = self.app.get('/admin')
		self.assertEqual(response.status_code, 302)

	def test_get_content_index(self):
		response = self.app.get('/content/')
		self.assertEqual(response.status_code, 200)

class HelperTest(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()

	def test_clip_image(self):
		pass

if __name__ == '__main__':
	unittest.main()