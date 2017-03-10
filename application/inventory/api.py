import requests
from .. import app

site = app.config['PRODUCT_SERVER']
version = 'api_v0.1'
headers = {'Content-Type': 'application/json'}


def load_categories():
    url = '%s/%s/product_categories' % (site, version)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def load_products(category_id):
    url = '%s/%s/product_category/%s/products' % (site, version, category_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def load_skus(product_id):
    url = '%s/%s/products/%s/skus' % (site, version, product_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        {}


def create_inventory(data={}):
    url = '%s/%s/inventories' % (site, version)
    response = requests.post(url, json=data, headers=headers)
    return response  # 201


def load_inventories(sku_id):
    url = '%s/%s/sku/%s/inventories' % (site, version, sku_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def load_inventories_by_code(code):
    url = '%s/%s/sku/%s/inventories_by_code' % (site, version, code)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def load_user_inventories(user_id, sku_id):
    url = '%s/%s/sku/%s/%s/inventories' % (site, version, user_id, sku_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def update_inventory(inv_id, data={}):
    url = '%s/%s/inventories/%s/edit' % (site, version, inv_id)
    response = requests.put(url, json=data, headers=headers)
    return response  # 200


def delete_inventory(inv_id):
    url = '%s/%s/inventories/%s' % (site, version, inv_id)
    response = requests.delete(url)
    return response  # 200


def load_inventory(inv_id):
    url = '%s/%s/inventories/%s' % (site, version, inv_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}


def update_sku(sku_id, data={}):
    url = '%s/%s/product_skus/%s/edit' % (site, version, sku_id)
    response = requests.put(url, json=data, headers=headers)
    return response   # 200


def update_sku_by_code(data={}):
    url = '%s/%s/product_skus/edit_by_code' % (site, version)
    response = requests.put(url, json=data, headers=headers)
    return response   # 200
