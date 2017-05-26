# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, url_for, request, current_app
from ..models import *
from flask_login import current_user
from ..wechat.models import WechatCall
from .. import cache


project_report = Blueprint('project_report', __name__, template_folder='templates')


@project_report.route("/index", methods=['GET'])
def index():
    page_size = int(request.args.get('page_size', 10))
    page_index = int(request.args.get('page', 1))
    project_reports = ProjectReport.query.filter(
        ProjectReport.app_id.in_(set([user.id for user in current_user.get_subordinate_dealers()]))).order_by(
        ProjectReport.created_at.desc()).paginate(page_index, per_page=page_size, error_out=True)
    return render_template('project_report/index.html', project_reports=project_reports)


@project_report.route("/<int:id>", methods=['GET'])
def show(id):
    pr = ProjectReport.query.get_or_404(id)
    return render_template('project_report/show.html', project_report=pr)


@project_report.route("/audit/<int:id>", methods=['GET', 'POST'])
def audit(id):
    pr = ProjectReport.query.get_or_404(id)
    if request.method == 'POST':
        pr.status = request.form.get("status")
        db.session.add(pr)
        db.session.commit()
        WechatCall.send_template_to_user(str(pr.app_id),
                                         "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0",
                                         {
                                             "first": {
                                                 "value": "您的项目报备状态已更新",
                                                 "color": "#173177"
                                             },
                                             "keyword1": {
                                                 "value": pr.report_no,
                                                 "color": "#173177"
                                             },
                                             "keyword2": {
                                                 "value": pr.status,
                                                 "color": "#173177"
                                             },
                                             "keyword3": {
                                                 "value": "",
                                                 "color": "#173177"
                                             },
                                             "remark": {
                                                 "value": "感谢您的使用！",
                                                 "color": "#173177"
                                             },
                                         },
                                         url_for('project_report_show', id=pr.id)
                                         )
        flash('项目报备申请审核成功', 'success')
        cache.delete_memoized(current_user.get_project_report_num)
        return redirect(url_for('project_report.index'))
    return render_template('project_report/audit.html', project_report=pr)


@project_report.route("/cancel/<int:id>", methods=['GET'])
def cancel(id):
    pr = ProjectReport.query.get_or_404(id)
    pr.status = "报备已取消"
    db.session.add(pr)
    db.session.commit()
    WechatCall.send_template_to_user(str(pr.app_id),
                                     "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0",
                                     {
                                         "first": {
                                             "value": "您的项目报备状态已更新",
                                             "color": "#173177"
                                         },
                                         "keyword1": {
                                             "value": pr.report_no,
                                             "color": "#173177"
                                         },
                                         "keyword2": {
                                             "value": pr.status,
                                             "color": "#173177"
                                         },
                                         "keyword3": {
                                             "value": "",
                                             "color": "#173177"
                                         },
                                         "remark": {
                                             "value": "感谢您的使用！",
                                             "color": "#173177"
                                         },
                                     },
                                     url_for('project_report_show', id=pr.id)
                                     )
    flash('项目报备申请取消成功', 'success')
    cache.delete_memoized(current_user.get_other_app_num)
    return redirect(url_for("project_report.index"))
