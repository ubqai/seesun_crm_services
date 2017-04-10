from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from .. import app
from ..models import User, AuthorityOperation, WebpageDescribe
from .forms import AccountLoginForm, AccountForm
from ..forms import BaseCsrfForm
from flask_login import logout_user, login_user, current_user
from ..wechat.models import WechatCall, WechatUserInfo

backstage_management = Blueprint('backstage_management', __name__, template_folder='templates')


# 单个使用@login_required
# 访问页面是否登入拦截
@backstage_management.before_app_request
def login_check():
    # url_rule
    # app.logger.info("into login_check")

    # 图片加载 or 无匹配请求
    if request.endpoint == "static" or request.endpoint is None:
        if request.endpoint is None:
            app.logger.info("LOGIN_CHECK None?  request.path [%s] , [%s]" % (request.path, request.endpoint))
        pass
    # 网站root访问 移动端
    # 所有移动端页面
    # wechat.mobile_ 使用微信相关JS的移动端页面
    else:
        if request.endpoint == "root" or \
                request.endpoint.startswith("mobile_") or \
                request.endpoint.startswith("wechat.mobile_") or \
                request.path.startswith("/mobile/"):

            # 微信自动登入拦截 -- code只能使用一次,所以绑定界面不能拦截
            if not request.endpoint == 'wechat.mobile_user_binding' and request.args.get("code") is not None:
                app.logger.info("微信端code自动登入拦截[%s]" % request.args.get("code"))
                try:
                    openid = WechatCall.get_open_id_by_code(request.args.get("code"))
                    wui = WechatUserInfo.query.filter_by(open_id=openid, is_active=True).first()
                    if wui is not None:
                        exists_binding_user = User.query.filter_by(id=wui.user_id).first()
                        if exists_binding_user is not None:
                            if exists_binding_user.id != current_user.id:
                                app.logger.info(
                                    "微信自动登入用户[%s],登出[%s]" % (exists_binding_user.nickname, current_user.nickname))
                                logout_user()
                            login_user(exists_binding_user)
                            app.logger.info("binding user login [%s] - [%s]" % (openid, exists_binding_user.nickname))
                except:
                    pass

            # 访问请求端的页面 不进行拦截
            if request.endpoint == "mobile_user_login" or request.endpoint == 'wechat.mobile_user_binding':
                pass
            # 未登入用户跳转登入界面
            elif not current_user.is_authenticated or current_user.user_or_origin != 2:
                app.logger.info("LOGIN_CHECK INTO MOBILE  request.path [%s] , [%s]" % (request.path, request.endpoint))
                # 后端界面
                flash("请登入后操作")
                session["login_next_url"] = request.path
                return redirect(url_for('mobile_user_login'))
        # 其他与微信服务器交互接口 不进行登入判断
        elif request.endpoint.startswith("wechat."):
            # 微信
            pass
        # 后端管理界面
        else:
            # 访问请求端的页面 不进行拦截
            if request.endpoint == "backstage_management.account_login":
                # 后端登入界面
                pass
            # 未登入用户跳转登入界面
            elif not current_user.is_authenticated or current_user.user_or_origin != 3:
                app.logger.info("LOGIN_CHECK INTO BACK END request.path [%s] , [%s]" % (request.path, request.endpoint))
                # 后端界面
                flash("请登入后操作")
                session["login_next_url"] = request.path
                return redirect(url_for('backstage_management.account_login'))

    return None


# 访问页面 是否有权限拦截
@backstage_management.before_app_request
def authority_check():
    # app.logger.info("into authority_check")
    if request.endpoint == "static" or request.endpoint is None \
            or current_user is None or not current_user.is_authenticated:
        pass
    else:
        if AuthorityOperation.is_authorized(current_user, request.endpoint, request.method) is False:
            flash("无权限登入页面 [%s] ,请确认" % WebpageDescribe.query.filter_by(endpoint=request.endpoint,
                                                                        method=request.method).first().describe)
            return redirect(url_for('backstage_management.index'))


@backstage_management.route('/index')
def index():
    app.logger.info("into index")
    form = AccountForm(obj=current_user, user_type=current_user.get_user_type_name(), meta={'csrf_context': session})
    if len(current_user.user_infos) == 0:
        pass
    else:
        ui = current_user.user_infos[0]
        form.name.data = ui.name
        form.address.data = ui.address
        form.phone.data = ui.telephone
        form.title.data = ui.title

    if current_user.sales_areas.first() is not None:
        form.sale_range.data = ",".join([s.name for s in current_user.sales_areas.all()])
    if current_user.departments.first() is not None:
        form.dept_ranges.data = ",".join([d.name for d in current_user.departments.all()])

    return render_template('backstage_management/index.html', form=form)


# -- login
# 需要区分pc or wechat ?
@backstage_management.route('/account/login', methods=['GET', 'POST'])
def account_login():
    if current_user.is_authenticated:
        if current_user.user_or_origin == 3:
            return redirect(url_for('backstage_management.index'))
        else:
            # 不运行前后端同时登入在一个WEB上
            app.logger.info("移动端用户[%s]自动登出,[%s][%s]" % (current_user.nickname, request.path, request.endpoint))
            logout_user()

    app.logger.info("account_login [%s]" % request.args)
    if request.method == 'POST':
        try:
            form = AccountLoginForm(request.form, meta={'csrf_context': session})
            if form.validate() is False:
                raise ValueError(form.errors)

            # 后台只能员工登入
            user = User.login_verification(form.email.data, form.password.data, 3)
            if user is None:
                raise ValueError("用户名或密码错误")

            login_valid_errmsg = user.check_can_login()
            if not login_valid_errmsg == "":
                raise ValueError(login_valid_errmsg)

            login_user(user)
            app.logger.info("后端用户[%s][%s]登入成功" % (user.email, user.nickname))
            # 直接跳转至需访问页面
            if session.get("login_next_url"):
                next_url = session.pop("login_next_url")
            else:
                next_url = url_for('backstage_management.index')
            return redirect(next_url)
        except Exception as e:
            app.logger.info("后端用户登入失败[%s]" % e)
            flash(e)
    else:
        form = AccountLoginForm(meta={'csrf_context': session})

    return render_template('backstage_management/account_login.html', form=form)


@backstage_management.route('/account/logout')
def account_logout():
    logout_user()
    return redirect(url_for('backstage_management.account_login'))


# 帐号信息管理
@backstage_management.route('/account/index')
def account_index():
    app.logger.info("into account_index")
    form = AccountForm(obj=current_user, user_type=current_user.get_user_type_name(), meta={'csrf_context': session})
    if len(current_user.user_infos) == 0:
        pass
    else:
        ui = current_user.user_infos[0]
        form.name.data = ui.name
        form.address.data = ui.address
        form.phone.data = ui.telephone
        form.title.data = ui.title

    if current_user.sales_areas.first() is not None:
        form.sale_range.data = ",".join([s.name for s in current_user.sales_areas.all()])
    if current_user.departments.first() is not None:
        form.dept_ranges.data = ",".join([d.name for d in current_user.departments.all()])

    return render_template('backstage_management/account_index.html', form=form)


# 帐号信息管理
@backstage_management.route('/account/password_update', methods=['POST'])
def account_password_update():
    app.logger.info("into account_password_update")
    try:
        form = BaseCsrfForm(request.form, meta={'csrf_context': session})
        if form.validate() is False:
            raise ValueError("非法提交,请通过正常页面进行修改")

        if request.form.get("email") != current_user.email:
            raise ValueError("非法提交,请通过正常页面进行修改")

        User.update_password(request.form.get("email"),
                             request.form.get("password_now"),
                             request.form.get("password_new"),
                             request.form.get("password_new_confirm"),
                             current_user.user_or_origin)

        flash("密码修改成功")
    except Exception as e:
        flash("密码修改失败: %s" % e)

    return redirect(url_for('backstage_management.account_index'))
