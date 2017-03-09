from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .. import app, db , login_manager
from ..models import *

import traceback,json
from .forms import *
from sqlalchemy import distinct
from flask_login import *

PAGINATION_PAGE_NUMBER=20

organization = Blueprint('organization', __name__, template_folder = 'templates')

# -- login 
#需要区分pc or wechat ?
@organization.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        if current_user.user_or_origin==3:
            return redirect(request.args.get('next') or url_for('mobile_user_index'))
        else:
            app.logger.info("移动端用户[%s]自动登出" % (current_user.nickname))
            logout_user()

    if request.method == 'POST':
        try:
            form = UserLoginForm(request.form)
            if form.validate()==False:
                raise ValueError("")

            #后台只能员工登入
            user=User.login_verification(form.email.data,form.password.data,3)
            if user==None:
                raise ValueError("用户名或密码错误")
            if not user.is_active:
                raise ValueError("用户异常,请联系管理员")
                
            login_user(user)
            return redirect(request.args.get('next') or url_for('organization.user_index'))
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
    form.reset_select_field()
    if form.user_type.data=="None":
        form.user_type.data="3"

    us = db.session.query(distinct(User.id)).filter(User.user_or_origin==form.user_type.data)
    if form.email.data:
        us = us.filter(User.email.like(form.email.data+"%"))
    if form.name.data:
        us = us.filter(User.nickname.like("%"+form.name.data+"%"))

    if form.user_type.data=="3":
        if form.dept_ranges.data and form.dept_ranges.data != [""]:
            dh_array=[dh_data.id for dh_data in form.dept_ranges.data]
        else:
            dh_array=[dh_data.id for dh_data in form.dept_ranges.query]
        us=us.join(User.departments).filter(DepartmentHierarchy.id.in_(dh_array))
    else:
        if form.sale_range.data and form.sale_range.data != "" and form.sale_range.data != "None":
            us=us.join(User.sales_areas).filter(SalesAreaHierarchy.id==form.sale_range.data.id)

    us=User.query.filter(User.id.in_(us)).order_by(User.id)
    pagination = us.paginate(page, PAGINATION_PAGE_NUMBER, False) 

    return render_template('organization/user_index.html',user_type=form.user_type.data,user_infos=pagination.items,pagination=pagination,form=form)


@organization.route('/user/new', methods=['GET', 'POST'])
def user_new():
    if request.method == 'POST':
        try:
            form = UserForm(request.form)
            form.reset_select_field()
            
            if form.nickname.data=="":
                form.nickname.data = form.name.data

            if form.validate()==False:
                app.logger.info("form valid fail: [%s]" % (form.errors))
                raise ValueError("")

            if User.query.filter_by(email=form.email.data).count()>0:
                raise ValueError("email已被注册,请更换!")

            ui=UserInfo(name=form.name.data,telephone=form.phone.data,address=form.address.data,title=form.title.data)

            u=User(email=form.email.data,user_or_origin=int(form.user_type.data),nickname=form.nickname.data)
            u.password = form.password.data
            u.user_infos.append(ui)

            if form.user_type.data=="3":
                for dh_data in form.dept_ranges.data:
                    dh =  DepartmentHierarchy.query.filter_by(id=dh_data.id).first()
                    if dh == None:
                        raise ValueError("所属部门错误[%s]" % (sah_id))
                    u.departments.append(dh)
            else:
                sah = SalesAreaHierarchy.query.filter_by(id=form.sale_range.data.id).first()
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
        form.reset_select_field()
        return render_template('organization/user_new.html',form=form)

@organization.route('/user/update/<int:user_id>', methods=['GET', 'POST'])
def user_update(user_id):
    u=User.query.filter_by(id=user_id).first()
    if u==None:
        return redirect(url_for('organization.user_search'))

    if request.method == 'POST':
        try:
            form = UserForm(request.form,user_type=u.user_or_origin)
            form.reset_select_field()

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
                dh_array=[dh_data.id for dh_data in form.dept_ranges.data]
                if sorted([i.id for i in u.departments]) != sorted(dh_array):
                    for d in u.departments:
                        u.departments.remove(d)
                    for d_id in dh_array:
                        u.departments.extend(form.dept_ranges.data)
            else:
                if u.sales_areas.first().id != form.sale_range.data.id:
                    sah=SalesAreaHierarchy.query.filter_by(id=form.sale_range.data.id).first()
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
        form.reset_select_field()
        if len(u.user_infos)==0:
            pass
        else:
            ui=u.user_infos[0]
            form.name.data=ui.name
            form.address.data=ui.address
            form.phone.data=ui.telephone
            form.title.data=ui.title

        if u.sales_areas.first()!=None:
            form.sale_range.default=u.sales_areas.first().id
        if u.departments.first()!=None:
            form.dept_ranges.default=u.departments.all()

        return render_template('organization/user_update.html',form=form,user_id=u.id)

@organization.route('/user/get_sale_range_by_parent/<int:level_grade>')
def get_sale_range_by_parent(level_grade):
    parent_id = request.args.get('parent_id', '__None')
    if parent_id=="__None":
        parent_id=None
    else:
        parent_id=int(parent_id)

    sa_array={}
    for sa in BaseForm.get_sale_range_by_parent(level_grade,parent_id):
        sa_array[sa.id]=sa.name
    json_data=json.dumps(sa_array)
    app.logger.info("return from get_sale_range_by_province [%s]" % (json_data))
    
    return json_data
