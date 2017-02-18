import urllib
import urllib.request
import json

def api_get(url):
	response = urllib.request.urlopen(url)
	return response
	#if response.getcode() == 200:
	#	return json.loads(response.read().decode())

def api_post(url, data = {}):
	data = json.dumps(data).encode()
	request = urllib.request.Request(url, data)
	request.add_header('Content-Type', 'application/json')
	response = urllib.request.urlopen(request)
	return response
	#if response.getcode() == 200:
	#	return json.loads(response.read().decode())