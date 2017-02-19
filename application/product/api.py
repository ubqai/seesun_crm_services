import urllib
import urllib.request
import json
from .. import app

site = app.config['PRODUCT_SERVER']

def api_get(url):
    response = urllib.request.urlopen(url)
    return response

def api_post(url, data = {}):
    data = json.dumps(data).encode()
    request = urllib.request.Request(url, data)
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request)
    return response

def load_products(category_id):
    url = '%s/api/product_category/%s/products' % (site, category_id)
    response = api_get(url)
    if response.getcode() == 200:
        return json.loads(response.read().decode())
    else:
        return []

def load_product(product_id):
    url = '%s/api/product/%s' % (site, product_id)
    response = api_get(url)
    if response.getcode() == 200:
        return json.loads(response.read().decode())
    else:
        {}

def load_skus(product_id):
    url = '%s/api/products/%s/skus' % (site, product_id)
    response = api_get(url)
    if response.getcode() == 200:
        return json.loads(response.read().decode())
    else:
        {}

def load_categories():
    url = '%s/api/product_categories' % site
    response = api_get(url)
    if response.getcode() == 200:
        return json.loads(response.read().decode())
    else: 
        return []

def load_category(category_id):
    url = '%s/api/product_categories/%s' % (site, category_id)
    response = api_get(url)
    if response.getcode() == 200:
        return json.loads(response.read().decode())[0]
    else:
        return {}

def load_features(category_id):
    return load_category(category_id).get('features') or []

def load_feature(feature_id):
    url = '%s/api/sku_feature/%s' % (site, feature_id)
    response = api_get(url)
    if response.getcode() == 200:
        return json.loads(response.read().decode())
    else:
        return {}