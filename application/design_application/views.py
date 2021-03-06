# -*- coding: utf-8 -*-
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from flask_login import current_user
from flask.helpers import make_response
from .. import app, cache
from ..helpers import object_list, save_upload_file, delete_file
from ..models import DesignApplication, ProjectReport
from .forms import DesignApplicationForm
from ..wechat.models import WechatCall

design_application = Blueprint('design_application', __name__, template_folder='templates')


@design_application.route('/index')
def index():
    applications = DesignApplication.query.all()
    return render_template('design_application/index.html', applications=applications)


@design_application.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    application = DesignApplication.query.get_or_404(id)
    project_report = ProjectReport.query.filter_by(report_no=application.filing_no).first()
    if request.method == 'POST':
        form = DesignApplicationForm(request.form)
        form.populate_obj(application)
        if request.form.get('status') == '申请通过':
            if request.files.get('dl_file'):
                file_path = save_upload_file(request.files.get('dl_file'))
                if file_path:
                    if application.dl_file:
                        delete_file(application.dl_file)
                    application.dl_file = file_path
                else:
                    flash('%s文件格式不合法' % str(request.files.get('dl_file').filename), 'danger')
                    return redirect(url_for('design_application.index'))
            flash('申请通过 %s' % str(request.files.get('dl_file').filename), 'success')
        elif request.form.get('status') == '申请不通过':
            flash('申请不通过', 'warning')
        application.save
        cache.delete_memoized(current_user.get_new_design_application_num)
        WechatCall.send_template_to_user(str(application.applicant_id),
                                         "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0",
                                         {
                                             "first": {
                                                 "value": "您的产品设计申请状态已更改",
                                                 "color": "#173177"
                                             },
                                             "keyword1": {
                                                 "value": application.filing_no,
                                                 "color": "#173177"
                                             },
                                             "keyword2": {
                                                 "value": application.status,
                                                 "color": "#173177"
                                             },
                                             "keyword3": {
                                                 "value": '',
                                                 "color": "#173177"
                                             },
                                             "remark": {
                                                 "value": "感谢您的使用！",
                                                 "color": "#173177"
                                             },
                                         },
                                         url_for('mobile_design_file', id=application.id)
                                         )
        return redirect(url_for('design_application.index'))
    else:
        form = DesignApplicationForm(obj=application)
    return render_template('design_application/edit.html', application=application, project_report=project_report,
                           form=form)


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
