# -*- coding: utf-8 -*-
import os, datetime, random
from flask import render_template, request
from werkzeug.utils import secure_filename
from PIL import Image

from . import app

def object_list(template_name, query, paginate_by = 20, **context):
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1 
    object_list = query.paginate(page, paginate_by)
    return render_template(template_name, object_list = object_list, **context)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Save upload file and return relative path
def save_upload_file(file):
    if allowed_file(file.filename):
        filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randrange(1000, 10000))
        try:
            new_filename = secure_filename(filename_prefix + file.filename)
        except:
            fname, fext = os.path.splitext(file.filename)
            new_filename = secure_filename(filename_prefix + fext)
        filepath = os.path.join(app.static_folder, 'upload', new_filename)
        file.save(filepath)
        return '/static/upload/%s' % new_filename
    return None
 
# This function is for clipping image by a specific size.
# First, check whether original image's size is bigger than specific.
# If yes, resize original image by proportion until width or height is equal to specific size.
# Final, crop the center region of image and save it.
def clip_image(filepath, size = (100, 100)):
    # file path should be absolute path
    image = Image.open(filepath)
    width = image.size[0]
    height = image.size[1]
    if width > size[0] and height > size[1]:
        if width/size[0] >= height/size[1]:
            x = int(size[1]*width/height)
            y = int(size[1])
            image = image.resize((x, y), Image.ANTIALIAS)
            dx = x - size[0]
            box = (dx/2, 0, x-dx/2, y)
            image = image.crop(box)
        else:
            x = int(size[0])    
            y = int(size[0]*height/width)
            image = image.resize((x, y), Image.ANTIALIAS)
            dy = y - size[1]
            box = (0, dy/2, x, y-dy/2)
            image = image.crop(box)
    else:
        dx = int(width - size[0])
        dy = int(height - size[1])
        box = (dx/2, dy/2, width-dx/2, height-dy/2)
        image = image.crop(box)
    image.save(filepath)