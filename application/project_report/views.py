# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, url_for, request, current_app
from ..models import *


project_report = Blueprint('project_report', __name__, template_folder='templates')


@project_report.route("/index", methods=['GET'])
def index():
    project_reports = ProjectReport.query.all()
    return render_template('project_report/index.html', project_reports=project_reports)


@project_report.route("/<int:id>", methods=['GET'])
def show(id):
    pr = ProjectReport.query.get_or_404(id)
    return render_template('project_report/show.html', project_report=pr)


@project_report.route("/audit/<int:id>", methods=['GET', 'POST'])
def audit(id):
    pr = ProjectReport.query.get_or_404(id)
    if request.method == 'POST':
        audit_content = {
            'sales_representative': request.form.get("sales_representative"),
            'sales_executive': request.form.get("sales_executive"),
            'sales_director': request.form.get("sales_director"),
            'is_authorized': request.form.get("is_authorized"),
            'authorization_date': request.form.get("authorization_date"),
            'authorization_no': request.form.get("authorization_no"),
        }
        pr.audit_content = audit_content
        pr.status = '项目报备审核通过'
        db.session.add(pr)
        db.session.commit()
        flash('项目报备申请审核成功', 'success')
        return redirect(url_for('project_report.index'))
    return render_template('project_report/audit.html', project_report=pr)


@project_report.route("/cancel/<int:id>", methods=['GET'])
def cancel(id):
    pr = ProjectReport.query.get_or_404(id)
    pr.status = "报备已取消"
    db.session.add(pr)
    db.session.commit()
    flash('项目报备申请取消成功', 'success')
    return redirect(url_for("project_report.index"))
