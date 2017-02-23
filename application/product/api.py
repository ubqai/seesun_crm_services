import requests
from .. import app

site = app.config['PRODUCT_SERVER']
version = 'api_v0.1'
headers = {'Content-Type': 'application/json'}

# resource :products, [:index, :show, :new, :edit, :delete]
def load_products(category_id):
    url = '%s/%s/product_category/%s/products' % (site, version, category_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
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
    response = requests.put(url, json = data, headers = headers)
    return response # 200

def delete_product(product_id):
    url = '%s/%s/products/%s' % (site, version, product_id)
    response = requests.delete(url)
    return response

# resource :skus, [:index, :show, :new, :edit, :delete]
def load_skus(product_id):
    url = '%s/%s/products/%s/skus' % (site, version, product_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        {}

def load_sku(product_id, sku_id):
    skus = load_skus(product_id).get('skus')
    if skus:
        for sku in skus:
            if sku.get('sku_id') == sku_id:
                return sku
    return {}

def create_sku(data = {}):
    url = '%s/%s/product_skus' % (site, version)
    response = requests.post(url, json = data, headers = headers)
    return response

def edit_sku(sku_id, data = {}):
    url = '%s/%s/product_skus/%s/edit' % (site, version, sku_id)
    response = requests.put(url, json = data, headers = headers)
    return response # 200

def delete_sku(sku_id):
    url = '%s/%s/product_skus/%s' % (site, version, sku_id)
    response = requests.delete(url)
    return response

# resource :categories, [:index, :show, :new, :edit]
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
    return response # 201

def edit_category(category_id, data = {}):
    url = '%s/%s/product_categories/%s/edit' % (site, version, category_id)
    response = requests.put(url, json = data, headers = headers)
    return response # 200

# resource :features, [:index, :show, :new, :edit]
def load_features(category_id):
    return load_category(category_id).get('features') or []

def load_feature(feature_id):
    url = '%s/%s/sku_feature/%s' % (site, version, feature_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def create_feature(data = {}):
    url = '%s/%s/sku_features' % (site, version)
    response = requests.post(url, json = data, headers = headers)
    return response

def edit_feature(feature_id, data = {}):
    url = '%s/%s/sku_features/%s/edit' % (site, version, feature_id)
    response = requests.put(url, json = data, headers = headers)
    return response

# resource :options, [:new, :edit]
def create_option(data = {}):
    url = '%s/%s/sku_options' % (site, version)
    response = requests.post(url, json = data, headers = headers)
    return response

def edit_option(option_id, data = {}):
    url = '%s/%s/sku_options/%s/edit' % (site, version, option_id)
    response = requests.put(url, json = data, headers = headers)
    return response