from flask import Blueprint, flash, redirect, render_template, request, url_for, session

from .. import app, db
from ..models import UserAndSaleArea, User, UserInfo, DepartmentHierarchy, SalesAreaHierarchy, AuthorityOperation, \
    WebpageDescribe

import traceback
import json
import datetime
from .forms import BaseForm, UserForm, UserSearchForm, RegionalSearchForm, BaseCsrfForm, \
    AuthoritySearchForm
from sqlalchemy import distinct
from flask_login import current_user

PAGINATION_PAGE_NUMBER = 20

organization = Blueprint('organization', __name__, template_folder='templates')


# --- user service ---
@organization.route('/user/index')
@organization.route('/user/index/<int:page>')
def user_index(page=1):
    form = UserSearchForm(request.args)
    form.reset_select_field()
    if form.user_type.data == "None":
        form.user_type.data = "3"

    us = db.session.query(distinct(User.id)).filter(User.user_or_origin == form.user_type.data)
    if form.email.data:
        us = us.filter(User.email.like(form.email.data + "%"))
    if form.name.data:
        us = us.filter(User.nickname.like("%" + form.name.data + "%"))

    if form.user_type.data == "3":
        if form.dept_ranges.data and form.dept_ranges.data != [""]:
            dh_array = [dh_data.id for dh_data in form.dept_ranges.data]
        else:
            dh_array = [dh_data.id for dh_data in form.dept_ranges.query]
        us = us.join(User.departments).filter(DepartmentHierarchy.id.in_(dh_array))
    else:
        if form.sale_range.data and form.sale_range.data != "" and form.sale_range.data != "None":
            us = us.join(User.sales_areas).filter(SalesAreaHierarchy.id == form.sale_range.data.id)

    us = User.query.filter(User.id.in_(us)).order_by(User.id)
    pagination = us.paginate(page, PAGINATION_PAGE_NUMBER, False)

    return render_template('organization/user_index.html', user_type=form.user_type.data, user_infos=pagination.items,
                           pagination=pagination, form=form)


@organization.route('/user/new', methods=['GET', 'POST'])
def user_new():
    if request.method == 'POST':
        try:
            form = UserForm(request.form, meta={'csrf_context': session})
            form.reset_select_field()

            if form.nickname.data == "":
                form.nickname.data = form.name.data

            if form.validate() is False:
                app.logger.info("form valid fail: [%s]" % form.errors)
                raise ValueError(form.errors)

            if User.query.filter_by(email=form.email.data).count() > 0:
                raise ValueError("邮箱[%s]已被注册,请更换!" % form.email.data)

            ui = UserInfo(name=form.name.data, telephone=form.phone.data, address=form.address.data,
                          title=form.title.data)

            u = User(email=form.email.data, user_or_origin=int(form.user_type.data), nickname=form.nickname.data)
            u.password = form.password.data
            u.user_infos.append(ui)

            if form.user_type.data == "3":
                app.logger.info("into 3 : [%s]" % form.dept_ranges.data)
                for dh_data in form.dept_ranges.data:
                    dh = DepartmentHierarchy.query.filter_by(id=dh_data.id).first()
                    if dh is None:
                        raise ValueError("所属部门错误[%s]" % dh_data.id)
                    u.departments.append(dh)
            else:
                app.logger.info("into 2 : [%s]" % form.sale_range.data.id)
                sah = SalesAreaHierarchy.query.filter_by(id=form.sale_range.data.id).first()
                if sah is None:
                    raise ValueError("销售区域错误[%s]" % form.sale_range.data.name)
                u.sales_areas.append(sah)

            u.save

            flash("添加经销商 %s,%s 成功" % (u.email, u.nickname))
            # return render_template('organization/user_new.html', form=form)
            return redirect(url_for('organization.user_index'))
        except Exception as e:
            flash(e)
            app.logger.info("organization.user_new exception [%s]" % (traceback.print_exc()))

            return render_template('organization/user_new.html', form=form)
    else:
        form = UserForm(meta={'csrf_context': session})
        form.reset_select_field()
        return render_template('organization/user_new.html', form=form)


@organization.route('/user/update/<int:user_id>', methods=['GET', 'POST'])
def user_update(user_id):
    u = User.query.filter_by(id=user_id).first()
    if u is None:
        flash("非法用户id")
        return redirect(url_for('organization.user_index'))
    auth_msg = current_user.authority_control_to_user(u)
    if auth_msg is not None:
        flash(auth_msg)
        return redirect(url_for('organization.user_index'))

    if request.method == 'POST':
        try:
            form = UserForm(request.form, user_type=u.user_or_origin, meta={'csrf_context': session})
            form.reset_select_field()

            app.logger.info("user_type[%s] , password[%s]" % (form.user_type.data, form.password_confirm.data))
            if form.nickname.data == "":
                form.nickname.data = form.name.data

            if form.validate() is False:
                app.logger.info("form valid fail: [%s]" % form.errors)
                raise ValueError(form.errors)

            u.email = form.email.data
            u.nickname = form.nickname.data

            if len(u.user_infos) == 0:
                ui = UserInfo()
            else:
                ui = u.user_infos[0]

            ui.name = form.name.data
            ui.telephone = form.phone.data
            ui.address = form.address.data
            ui.title = form.title.data

            if len(u.user_infos) == 0:
                u.user_infos.append(ui)

            if u.user_or_origin == 3:
                dh_array = [dh_data.id for dh_data in form.dept_ranges.data]
                if sorted([i.id for i in u.departments]) != sorted(dh_array):
                    for d in u.departments:
                        u.departments.remove(d)
                    # for d_id in dh_array:
                    # u.departments.append(DepartmentHierarchy.query.filter_by(id=d_id).first())
                    u.departments.extend(form.dept_ranges.data)
            else:
                if u.sales_areas.count() == 0 or u.sales_areas.first().id != form.sale_range.data.id:
                    if not u.sales_areas.count() == 0:
                        u.sales_areas.remove(u.sales_areas.first())
                    sah = SalesAreaHierarchy.query.filter_by(id=form.sale_range.data.id).first()
                    u.sales_areas.append(sah)

            u.save

            flash("修改经销商 %s,%s 成功" % (u.email, u.nickname))
            # return render_template('organization/user_update.html', form=form, user_id=u.id)
            return redirect(url_for('organization.user_update', user_id=u.id))
        except ValueError as e:
            flash(e)
            return render_template('organization/user_update.html', form=form, user_id=u.id)
    else:
        form = UserForm(obj=u, user_type=u.user_or_origin, meta={'csrf_context': session})
        form.reset_select_field()
        if len(u.user_infos) == 0:
            pass
        else:
            ui = u.user_infos[0]
            form.name.data = ui.name
            form.address.data = ui.address
            form.phone.data = ui.telephone
            form.title.data = ui.title

        if u.sales_areas.first() is not None:
            form.sale_range.default = u.sales_areas.first().id
        if u.departments.first() is not None:
            form.dept_ranges.default = u.departments.all()

        return render_template('organization/user_update.html', form=form, user_id=u.id)


@organization.route('/user/get_sale_range_by_parent/<int:level_grade>')
def get_sale_range_by_parent(level_grade):
    parent_id = request.args.get('parent_id', '__None')
    if parent_id == "__None":
        parent_id = None
    else:
        parent_id = int(parent_id)

    sa_array = {}
    for sa in BaseForm.get_sale_range_by_parent(level_grade, parent_id):
        sa_array[sa.id] = sa.name
    json_data = json.dumps(sa_array)
    app.logger.info("return from get_sale_range_by_province [%s]" % json_data)

    return json_data


# --- regional_and_team service ---
@organization.route('/user/regional_and_team/index')
def regional_and_team_index():
    form = RegionalSearchForm(request.args)
    form.reset_select_field()

    sah_infos = {}
    app.logger.info("regional.data [%s]" % form.regional.data)
    if not form.regional.data:
        sah_search = form.regional.query
    else:
        sah_search = form.regional.data

    for sah in sah_search:
        # 每个区域只有一个总监
        leader_info = UserAndSaleArea.query.filter(UserAndSaleArea.parent_id == None,
                                                   UserAndSaleArea.sales_area_id == sah.id).first()
        if leader_info is None:
            leader = (-1, "无")
        else:
            u = User.query.filter(User.id == leader_info.user_id).first()
            leader = (u.id, u.nickname)

        sah_infos[sah.id] = {"regional_name": sah.name, "leader_info": leader,
                             "regional_province_infos": SalesAreaHierarchy.get_team_info_by_regional(sah.id)}

    return render_template('organization/regional_and_team_index.html', form=form, sah_infos=sah_infos)


@organization.route('/user/regional/manage_leader/<int:sah_id>', methods=['GET', 'POST'])
def regional_manage_leader(sah_id):
    sah = SalesAreaHierarchy.query.filter_by(id=sah_id).first()
    if sah is None:
        flash("非法区域id[%d]" % sah_id)
        return redirect(url_for('organization.regional_and_team_index'))

    if request.method == 'POST':
        try:
            form = BaseCsrfForm(request.form, meta={'csrf_context': session})
            if form.validate() is False:
                flash(form.errors)
                return redirect(url_for('organization.regional_and_team_index'))

            user_id = int(request.form.get("user_id"))
            leader_info = UserAndSaleArea.query.filter_by(sales_area_id=sah.id, parent_id=None).first()
            if leader_info is not None and leader_info.user_id == user_id:
                flash("未修改区域负责人请确认")
                return redirect(url_for('organization.regional_manage_leader', sah_id=sah.id))

            # 删除所有销售团队信息
            if leader_info is not None:
                for regional_info in SalesAreaHierarchy.query.filter_by(parent_id=sah.id).all():
                    team_info = UserAndSaleArea.query.filter(UserAndSaleArea.parent_id == leader_info.user_id,
                                                             UserAndSaleArea.sales_area_id == regional_info.id).first()
                    if team_info is not None:
                        db.session.delete(team_info)

                db.session.delete(leader_info)

            # add data proc
            app.logger.info("add new user[%s] proc" % user_id)
            u_add = User.query.filter_by(id=user_id).first()
            u_add.sales_areas.append(sah)
            db.session.add(u_add)

            db.session.commit()
            flash("区域[%s] 负责人修改成功" % sah.name)
            return redirect(url_for('organization.regional_and_team_index'))
        except Exception as e:
            flash("区域[%s] 负责人修改失败:[%s]" % (sah.name, e))
            db.session.rollback()
            return redirect(url_for('organization.regional_manage_leader', sah_id=sah.id))
    else:
        form = BaseCsrfForm(meta={'csrf_context': session})
        us = db.session.query(User).join(User.departments) \
            .filter(User.user_or_origin == 3) \
            .filter(DepartmentHierarchy.name == "销售部") \
            .order_by(User.id)
        app.logger.info("regional_manage_leader us get count: [%d]" % (us.count()))
        user_infos = {}
        for u in us.all():
            uasa = UserAndSaleArea.query.filter(UserAndSaleArea.user_id == u.id,
                                                UserAndSaleArea.parent_id != None).first()
            if uasa is not None:
                continue

            choose = 0
            if u.sales_areas.filter(SalesAreaHierarchy.id == sah.id).count() > 0:
                choose = 1

            user_infos[u.id] = {"choose": choose, "name": u.nickname}

        sorted_user_infos = sorted(user_infos.items(), key=lambda p: p[1]["choose"], reverse=True)
        app.logger.info("sorted_user_infos [%s]" % sorted_user_infos)

        return render_template('organization/regional_manage_leader.html', sorted_user_infos=sorted_user_infos,
                               sah_id=sah.id,
                               regional_province_infos=SalesAreaHierarchy.get_team_info_by_regional(sah.id), form=form)


@organization.route('/user/regional/manage_team/<int:sah_id>-<int:leader_id>-<int:region_province_id>',
                    methods=['GET', 'POST'])
def regional_manage_team(sah_id, leader_id, region_province_id):
    app.logger.info("regional_manage_team [%d],[%d],[%d]" % (sah_id, leader_id, region_province_id))
    sah = SalesAreaHierarchy.query.filter_by(id=sah_id).first()
    if sah is None:
        flash("非法区域id[%d]" % sah_id)
        return redirect(url_for('organization.regional_and_team_index'))

    leader = User.query.filter_by(id=leader_id).first()
    if leader is None:
        flash("非法负责人id[%d]" % leader_id)
        return redirect(url_for('organization.regional_and_team_index'))

    if request.method == 'POST':
        try:
            form = BaseCsrfForm(request.form, meta={'csrf_context': session})
            if form.validate() is False:
                flash(form.errors)
                return redirect(url_for('organization.regional_and_team_index'))

            user_id = int(request.form.get("user_id"))
            team_info = UserAndSaleArea.query.filter(UserAndSaleArea.sales_area_id == region_province_id,
                                                     UserAndSaleArea.parent_id != None).first()
            if team_info is not None and team_info.user_id == user_id:
                flash("未修改销售团队请确认")
                return redirect(url_for('organization.regional_manage_team', sah_id=sah.id, leader_id=leader_id,
                                        region_province_id=region_province_id))

            # exists data proc
            if team_info is not None:
                db.session.delete(team_info)

            app.logger.info("add new user[%s] proc" % (user_id))
            uasa = UserAndSaleArea(user_id=user_id, sales_area_id=region_province_id, parent_id=leader.id,
                                   parent_time=datetime.datetime.now())
            db.session.add(uasa)

            db.session.commit()
            flash("区域[%s] 负责人[%s] 销售团队修改成功" % (sah.name, leader.nickname))
            return redirect(url_for('organization.regional_and_team_index'))
        except Exception as e:
            flash("区域[%s] 负责人[%s] 销售团队修改成功:[%s]" % (sah.name, leader.nickname, e))
            db.session.rollback()
            return redirect(url_for('organization.regional_manage_team', sah_id=sah.id, leader_id=leader_id,
                                    region_province_id=region_province_id))
    else:
        form = BaseCsrfForm(meta={'csrf_context': session})
        us = db.session.query(User).join(User.departments) \
            .filter(User.user_or_origin == 3) \
            .filter(DepartmentHierarchy.name == "销售部") \
            .order_by(User.id)
        app.logger.info("regional_manage_team us get count: [%d]" % (us.count()))
        user_infos = {}
        for u in us.all():
            # 排除负责人
            uasa = UserAndSaleArea.query.filter(UserAndSaleArea.user_id == u.id,
                                                UserAndSaleArea.parent_id == None).first()
            if uasa is not None:
                continue

            # 排除其他负责人的团队成员
            uasa = UserAndSaleArea.query.filter(UserAndSaleArea.user_id == u.id,
                                                UserAndSaleArea.parent_id != leader.id).first()
            if uasa is not None:
                continue

            choose = 0
            if u.sales_areas.filter(SalesAreaHierarchy.id == region_province_id).count() > 0:
                choose = 1

            user_infos[u.id] = {"choose": choose, "name": u.nickname}

        sorted_user_infos = sorted(user_infos.items(), key=lambda p: p[1]["choose"], reverse=True)
        app.logger.info("sorted_user_infos [%s]" % sorted_user_infos)

        return render_template('organization/regional_manage_team.html', sorted_user_infos=sorted_user_infos,
                               sah_id=sah.id, leader_id=leader.id, region_province_id=region_province_id, form=form)


@organization.route('/user/regional/manage_province/<int:sah_id>', methods=['GET', 'POST'])
def regional_manage_province(sah_id):
    sah = SalesAreaHierarchy.query.filter_by(id=sah_id).first()
    if sah is None:
        flash("非法区域id[%d]" % sah_id)
        return redirect(url_for('organization.regional_and_team_index'))

    if request.method == 'POST':
        try:
            form = BaseCsrfForm(request.form, meta={'csrf_context': session})
            if form.validate() is False:
                flash(form.errors)
                return redirect(url_for('organization.regional_and_team_index'))

            province_id_array = request.form.getlist("province_id")
            app.logger.info("choose province_arrays: [%s]" % province_id_array)
            delete_exists_count = 0
            # 先对已有记录进行删除
            for exists_province in SalesAreaHierarchy.query.filter_by(parent_id=sah.id).all():
                if exists_province.id in province_id_array:
                    app.logger.info("has existed province[%s] not proc" % exists_province.name)
                    province_id_array.remove(exists_province.id)
                else:
                    app.logger.info("delete existed province[%s]" % exists_province.name)
                    # 删除对应销售团队
                    uasa = UserAndSaleArea.query.filter_by(sales_area_id=exists_province.id).first()
                    if uasa is not None:
                        db.session.delete(uasa)

                    exists_province.parent_id = None
                    db.session.add(exists_province)
                    delete_exists_count += 1

            if delete_exists_count == 0 and len(province_id_array) == 0:
                flash("未修改销售(省)请确认")
                return redirect(url_for('organization.regional_manage_province', sah_id=sah.id))

            # 新增记录
            for add_province_id in province_id_array:
                add_province = SalesAreaHierarchy.query.filter_by(id=add_province_id).first()
                if add_province is None:
                    raise ValueError("no SalesAreaHierarchy found? [%s]" % add_province_id)

                # 删除对应销售团队
                uasa = UserAndSaleArea.query.filter_by(sales_area_id=add_province.id).first()
                if uasa is not None:
                    db.session.delete(uasa)

                add_province.parent_id = sah.id
                db.session.add(add_province)

            db.session.commit()
            flash("区域[%s] 区域(省)修改成功" % sah.name)
            return redirect(url_for('organization.regional_and_team_index'))
        except Exception as e:
            flash(e)
            db.session.rollback()
            return redirect(url_for('organization.regional_manage_province', sah_id=sah.id))
    else:
        form = BaseCsrfForm(meta={'csrf_context': session})
        province_info = {}
        for sah_province in BaseForm().get_sale_range_by_parent(3, None):
            if sah_province.parent_id == sah.id:
                sah_up_name = sah.name
                choose = 1
            else:
                sah_province_up = SalesAreaHierarchy.query.filter_by(id=sah_province.parent_id).first()
                if sah_province_up is None:
                    sah_up_name = "无"
                else:
                    sah_up_name = sah_province_up.name
                choose = 0

            province_info[sah_province.id] = {"name": sah_province.name, "up_name": sah_up_name, "choose": choose}

        sorted_province_info = sorted(province_info.items(), key=lambda p: p[1]["choose"], reverse=True)
        app.logger.info("sorted_province_info [%s]" % sorted_province_info)
        return render_template('organization/regional_manage_province.html', sah_id=sah.id,
                               sorted_province_info=sorted_province_info, form=form)


# 权限管理
@organization.route('/authority/index', methods=['GET', 'POST'])
def authority_index():
    form = AuthoritySearchForm(request.form, meta={'csrf_context': session})

    wd_infos = WebpageDescribe.query.filter_by(validate_flag=True)
    if form.web_types.data:
        wd_infos = wd_infos.filter(WebpageDescribe.type.in_(form.web_types.data))
    if form.describe.data:
        wd_infos = wd_infos.filter(WebpageDescribe.describe.ilike('%' + form.describe.data + '%'))
    if form.roles.data and form.roles.data != ['']:
        app.logger.info("roles data %s" % form.roles.data)
        wd_infos = wd_infos.join(AuthorityOperation).filter(AuthorityOperation.role_id.in_(form.roles.data))

    wd_infos = wd_infos.order_by(WebpageDescribe.type, WebpageDescribe.endpoint).all()
    return render_template('organization/authority_index.html', form=form, wd_infos=wd_infos)


@organization.route('/authority/to_role/<int:webpage_id>', methods=['GET', 'POST'])
def authority_to_role(webpage_id):
    form = AuthoritySearchForm(request.form, meta={'csrf_context': session})
    wd = WebpageDescribe.query.filter_by(id=webpage_id).first()
    page_info = (webpage_id, wd.describe)

    if request.method == "POST":
        try:
            if form.validate() is False:
                flash(form.errors)

            app.logger.info(request.form.getlist("role_id"))
            # 处理现有授权
            add_rolelist = [int(role_id) for role_id in request.form.getlist("role_id")]
            for ao in AuthorityOperation.query.filter_by(webpage_id=webpage_id, flag="Y").all():
                if ao.id in add_rolelist:
                    add_rolelist.remove(ao.id)
                else:
                    ao.flag = "N"
                    db.session.add(ao)

            # 处理需要增加授权的role
            for add_role_id in add_rolelist:
                ao = AuthorityOperation.query.filter_by(webpage_id=webpage_id, role_id=add_role_id).first()
                if ao is not None:
                    ao.flag = "Y"
                    ao.time = datetime.datetime.now()
                else:
                    ao = AuthorityOperation(webpage_id=webpage_id, role_id=add_role_id, flag="Y")

                db.session.add(ao)

            db.session.commit()
            flash("授权成功")
            return redirect(url_for('organization.authority_index'))
        except Exception as e:
            db.sesion.rollback()
            flash("授权失败: %s" % e)
            return redirect(url_for('organization.authority_to_role', webpage_id=webpage_id))
    else:
        role_infos = []
        for role_id, role_name in User.get_all_roles():
            ao = AuthorityOperation.query.filter_by(webpage_id=webpage_id, role_id=role_id).first()
            choose = 0
            if ao is not None and ao.flag == "Y":
                choose = 1
            role_infos.append((role_id, role_name, choose))

        sorted_role_infos = sorted(role_infos, key=lambda p: p[2], reverse=True)
        return render_template('organization/authority_to_role.html', form=form, sorted_role_infos=sorted_role_infos,
                               page_info=page_info)
