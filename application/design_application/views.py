# -*- coding: utf-8 -*-
from flask     import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from flask.helpers import make_response
from ..        import app
from ..helpers import object_list, save_upload_file
from ..models  import DesignApplication
from .forms    import DesignApplicationForm

design_application = Blueprint('design_application', __name__, template_folder = 'templates')

@design_application.route('/index')
def index():
	applications = DesignApplication.query.all()
	return render_template('design_application/index.html', applications = applications)


@design_application.route('/<int:id>/edit', methods = ['GET', 'POST'])
def edit(id):
	application = DesignApplication.query.get_or_404(id)
	if request.method == 'POST':
		form = DesignApplicationForm(request.form)
		if request.form.get('status') == '申请通过':
			if request.files.get('dl_file'):
				application.status = '申请通过'
				file_path = save_upload_file(request.files.get('dl_file'))
				if file_path:
					application.dl_file = file_path
					application.save
					flash('申请通过', 'success')
				else:
					flash('设计文件上传失败', 'danger')
					return redirect(url_for('design_application.edit', id = application.id))
			else:
				flash('设计文件未上传', 'danger')
				return redirect(url_for('design_application.edit', id = application.id))
		elif request.form.get('status') == '申请不通过':
			application.status = '申请不通过'
			application.save
			flash('申请不通过', 'warning')
		return redirect(url_for('design_application.index'))
	else:
		form = DesignApplicationForm(obj = application)
	return render_template('design_application/edit.html', application = application, form = form)

@design_application.route('/<int:id>/dl_file')
def dl_file(id):
	application = DesignApplication.query.get_or_404(id)
	response = make_response(send_file(app.config['APPLICATION_DIR'] + application.dl_file))
	response.headers['Content-Disposition'] = 'attachment; filename = %s' % application.dl_file.rsplit('/', 1)[1]
	return response


@design_application.route('/<int:id>/ul_file')
def ul_file(id):
	application = DesignApplication.query.get_or_404(id)
	response = make_response(send_file(app.config['APPLICATION_DIR'] + application.ul_file))
	response.headers['Content-Disposition'] = 'attachment; filename = %s' % application.ul_file.rsplit('/', 1)[1]
	return response