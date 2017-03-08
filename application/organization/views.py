from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .. import app, db , login_manager , bcrypt
from ..models import *

import traceback
from .forms import *
from sqlalchemy import distinct
from flask_login import *

PAGINATION_PAGE_NUMBER=20

organization = Blueprint('organization', __name__, template_folder = 'templates')

# -- login 
#需要区分pc or wechat ?
@organization.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        try:
            form = UserLoginForm(request.form)
            if form.validate()==False:
                raise ValueError("")

            #后台只能员工登入
            user=User.login_verification(form.email.data,form.password.data,3)
            if user==None:
                raise ValueError("用户名或密码错误")

            login_user(user)
            return redirect(url_for('organization.user_index'))
        except Exception as e:
            flash(e)
    else:
        form = UserLoginForm()

    return render_template('organization/user_login.html',form=form)

@organization.route('/user/logout')
def user_logout():
    logout_user()
    return redirect(url_for('organization.user_login'))

# --- user service ---
@organization.route('/user/index')
@organization.route('/user/index/<int:page>')
def user_index(page=1):
    form = UserSearchForm(request.args)
    app.logger.info("organization.user_index form: [%s]" % (form))
    if form.user_type.data=="None":
        form.user_type.data="3"

    us = db.session.query(distinct(User.id)).filter(User.user_or_origin==form.user_type.data)
    if form.email.data:
        us = us.filter(User.email.like(form.email.data+"%"))
    if form.name.data:
        us = us.filter(User.nickname.like("%"+form.name.data+"%"))
    #how to search in many-to-many

    app.logger.info("user_type [%s]" % form.user_type.data)
    if form.user_type.data=="3":
        app.logger.info("into dept_ranges [%s]" % (form.dept_ranges.data))
        if form.dept_ranges.data and form.dept_ranges.data != ["-1"] and form.dept_ranges.data != [""]:
            us=us.join(User.departments).filter(DepartmentHierarchy.id.in_(form.dept_ranges.data))
    else:
        app.logger.info("into sale_range [%s]" % form.sale_range.data)
        if form.sale_range.data and form.sale_range.data != "-1" and form.sale_range.data != "None":
            us=us.join(User.sales_areas).filter(SalesAreaHierarchy.id==form.sale_range.data)

    us=User.query.filter(User.id.in_(us)).order_by(User.id)
    pagination = us.paginate(page, PAGINATION_PAGE_NUMBER, False) 

    return render_template('organization/user_index.html',user_type=form.user_type.data,user_infos=pagination.items,pagination=pagination,form=form)


@organization.route('/user/new', methods=['GET', 'POST'])
def user_new():
    if request.method == 'POST':
        try:
            form = UserForm(request.form)

            if form.nickname.data=="":
                form.nickname.data = form.name.data

            if form.validate()==False:
                app.logger.info("form valid fail: [%s]" % (form.errors))
                raise ValueError("")

            if User.query.filter_by(email=form.email.data).count()>0:
                raise ValueError("email已被注册,请更换!")

            ui=UserInfo(name=form.name.data,telephone=form.phone.data,address=form.address.data,title=form.title.data)

            u=User(email=form.email.data,user_or_origin=int(form.user_type.data),nickname=form.nickname.data)
            u.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            u.user_infos.append(ui)

            if form.user_type.data=="3":
                for d_id in form.dept_ranges.data:
                    dh =  DepartmentHierarchy.query.filter_by(id=int(d_id)).first()
                    if dh == None:
                        raise ValueError("所属部门错误[%s]" % (sah_id))
                    u.departments.append(dh)
            else:
                sah = SalesAreaHierarchy.query.filter_by(id=int(form.sale_range.data)).first()
                if sah==None:
                    raise ValueError("销售区域错误[%s]" % (sah_id))
                u.sales_areas.append(sah)

            u.save

            flash("添加经销商 %s,%s 成功" % (u.email,u.nickname))
            return render_template('organization/user_new.html',form=form)
        except Exception as e:
            flash(e)
            app.logger.info("organization.user_new exception [%s]" % (traceback.print_exc()))

            return render_template('organization/user_new.html',form=form)
    else:
        form = UserForm()
        return render_template('organization/user_new.html',form=form)

@organization.route('/user/update/<int:user_id>', methods=['GET', 'POST'])
def user_update(user_id):
    u=User.query.filter_by(id=user_id).first()
    if u==None:
        return redirect(url_for('organization.user_search'))

    if request.method == 'POST':
        try:
            form = UserForm(request.form,user_type=u.user_or_origin)

            app.logger.info("user_type[%s] , password[%s]" % (form.user_type.data,form.password_confirm.data))
            if form.nickname.data=="":
                form.nickname.data = form.name.data

            if form.validate()==False:
                app.logger.info("form valid fail: [%s]" % (form.errors))
                raise ValueError("")

            u.email=form.email.data
            u.nickname=form.nickname.data

            if len(u.user_infos)==0:
                ui = UserInfo()
            else:
                ui = u.user_infos[0]

            ui.name=form.name.data
            ui.telephone=form.phone.data
            ui.address=form.address.data
            ui.title=form.title.data

            if len(u.user_infos)==0:
                u.user_infos.append(ui)

            if u.user_or_origin==3:
                if sorted([str(i.id) for i in u.departments]) != sorted(form.dept_ranges.data):
                    for d in u.departments:
                        u.departments.remove(d)
                    for d_id in form.dept_ranges.data:
                        dh=DepartmentHierarchy.query.filter_by(id=int(d_id)).first()
                        u.departments.append(dh)
            else:
                if u.sales_areas.first().id != int(form.sale_range.data):
                    sah=SalesAreaHierarchy.query.filter_by(id=int(form.sale_range.data)).first()
                    u.sales_areas.remove(u.sales_areas.first())
                    u.sales_areas.append(sah)

            u.save

            flash("修改经销商 %s,%s 成功" % (u.email,u.nickname))
            return render_template('organization/user_update.html',form=form,user_id=u.id)
        except Exception as e:
            flash(e)
            return render_template('organization/user_update.html',form=form,user_id=u.id)
    else:
        form = UserForm(obj=u,user_type=u.user_or_origin)
        if len(u.user_infos)==0:
            pass
        else:
            ui=u.user_infos[0]
            form.name.data=ui.name
            form.address.data=ui.address
            form.phone.data=ui.telephone
            form.title.data=ui.title

        if u.sales_areas.first()!=None:
            form.sale_range.data=str(u.sales_areas.first().id)
        if u.departments.first()!=None:
            form.dept_ranges.data=[str(d.id) for d in u.departments]

        return render_template('organization/user_update.html',form=form,user_id=u.id)