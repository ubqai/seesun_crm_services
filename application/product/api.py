import urllib
import urllib.request
import requests
import json
from .. import app

site = app.config['PRODUCT_SERVER']
version = 'api_v0.1'
headers = {'Content-Type': 'application/json'}

def api_post(url, data = {}):
    data = json.dumps(data).encode()
    request = urllib.request.Request(url, data)
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request)
    return response

# resource :products, [:index, :show, :new, :edit, :delete]
def load_products(category_id):
    url = '%s/%s/product_category/%s/products' % (site, version, category_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.status_code
    else:
        return []

def load_product(product_id):
    url = '%s/%s/product/%s' % (site, version, product_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        {}

def create_product(data = {}):
    url = '%s/%s/products' % (site, version)
    response = requests.post(url, json = data, headers = headers)
    return response # 201

def edit_product(product_id, data):
    url = '%s/%s/products/%s/edit' % (site, version, product_id)
    return api_post(url, data) # 200

def delete_product(product_id):
    url = '%s/%s/products/%s' % (site, version, product_id)
    pass

# resource :skus, [:index, :show, :new, :edit, :delete]
def load_skus(product_id):
    url = '%s/%s/products/%s/skus' % (site, version, product_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        {}

# resource :categories, [:index, :show, :new, :edit, :delete]
def load_categories():
    url = '%s/%s/product_categories' % (site, version)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else: 
        return []

def load_category(category_id):
    url = '%s/%s/product_categories/%s' % (site, version, category_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]
    else:
        return {}

def create_category(data = {}):
    url = '%s/%s/product_categories' % (site, version)
    response = requests.post(url, json = data, headers = headers)
    return response

def edit_category(category_id, data = {}):
    url = '%s/%s/product_categories/%s/edit' % (site, version, category_id)
    response = requests.put(url, json = data, headers = headers)
    return response # 200

def delete_category(category_id):
    pass

# resource :features, [:index, :show, :new, :edit, :delete]
def load_features(category_id):
    return load_category(category_id).get('features') or []

def load_feature(feature_id):
    url = '%s/%s/sku_feature/%s' % (site, version, feature_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# resource :options, [:index, :show, :new, :edit, :delete]