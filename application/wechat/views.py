from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from .models import WechatAccessToken, app, WECHAT_SERVER_AUTHENTICATION_TOKEN, WechatCall, WechatUserInfo, \
    WechatPushMsg
from ..organization.forms import WechatUserLoginForm
from ..models import User, TrackingInfo, Contract
from flask_login import login_user, current_user, logout_user
import hashlib

import xml.dom.minidom
import datetime

wechat = Blueprint('wechat', __name__, template_folder='templates')


@wechat.route('/mobile/verification', methods=['GET', 'POST'])
def mobile_verification():
    if request.method == 'POST':
        try:
            qrcode_token = request.form.get("text-verification", None)
            if qrcode_token is None or qrcode_token == "":
                raise ValueError("请传入扫描结果")

            app.logger.info("wechat.mobile_verification: [%s]", qrcode_token)
            ti = TrackingInfo.query.filter_by(qrcode_token=qrcode_token).first()
            if ti is None:
                raise ValueError("无此二维码记录")

            contract = Contract.query.filter_by(contract_no=ti.contract_no).first()
            if contract is None or contract.order_id is None:
                raise ValueError("二维码记录异常")

            flash('校验成功', 'success')
            return redirect(url_for('mobile_contract_show', id=contract.order_id))
        except Exception as e:
            flash('校验失败,%s' % e)
            return redirect(url_for('wechat.mobile_verification'))
    else:
        wechat_info = None
        try:
            wechat_info = WechatAccessToken.get_js_api_sign(request.url)
        except Exception as e:
            flash('摄像头授权获取失败,请刷新重试 %s' % e)

        return render_template('wechat/mobile_verification.html', wechat_info=wechat_info)


@wechat.route('/mobile/user_binding', methods=['GET', 'POST'])
def mobile_user_binding():
    if request.method == 'POST':
        try:
            if current_user.is_authenticated:
                logout_user()

            form = WechatUserLoginForm(request.form, meta={'csrf_context': session})
            if not form.validate():
                app.logger.info("form valid fail: [%s]" % form.errors)
                raise ValueError("")

            # 微信只能经销商登入
            user = User.login_verification(form.email.data, form.password.data, 2)
            if user is None:
                raise ValueError("用户名或密码错误")

            login_valid_errmsg = user.check_can_login()
            if not login_valid_errmsg == "":
                raise ValueError(login_valid_errmsg)

            wui = WechatUserInfo.query.filter_by(open_id=form.openid.data, user_id=user.id).first()
            if wui is None:
                wui = WechatUserInfo(open_id=form.openid.data, user_id=user.id, is_active=True)
            else:
                wui.is_active = True
                wui.active_time = datetime.datetime.now()

            wui.save()
            app.logger.info("insert into WechatUserInfo [%s]-[%s]" % (form.openid.data, user.id))

            login_user(user)
            app.logger.info("mobile login success [%s]" % user.nickname)
            return redirect(url_for('mobile_index'))
        except Exception as e:
            flash("绑定失败,%s" % e)
            return render_template('wechat/mobile_user_binding.html', form=form)
    else:
        app.logger.info("mobile_user_binding [%s][%s]" % (request.args, request.args.get("code")))
        openid = ""
        if request.args.get("code") is None:
            flash("请关闭页面后,通过微信-绑定用户进入此页面")
        else:
            try:
                openid = WechatCall.get_open_id_by_code(request.args.get("code"))
                app.logger.info("get openid[%s] by code[%s]" % (openid, request.args.get("code")))
                wui = WechatUserInfo.query.filter_by(open_id=openid, is_active=True).first()
                if wui is not None:
                    exists_binding_user = User.query.filter_by(id=wui.user_id).first()
                    if exists_binding_user is not None:  # normal
                        if current_user.is_authenticated:  # has login
                            if current_user != exists_binding_user:  # not same user
                                logout_user()
                                login_user(exists_binding_user)
                                app.logger.info("mobile login success [%s]" % exists_binding_user.nickname)
                            else:
                                app.logger.info("mobile has login [%s]" % exists_binding_user.nickname)
                        else:
                            login_user(exists_binding_user)
                            app.logger.info("mobile login success [%s]" % exists_binding_user.nickname)

                        return redirect(url_for('mobile_index'))
            except Exception as e:
                flash("%s,请重新通过微信-绑定用户进入此页面" % e)

        form = WechatUserLoginForm(openid=openid, meta={'csrf_context': session})
        return render_template('wechat/mobile_user_binding.html', form=form)


@wechat.route("/server/authentication", methods=['GET', 'POST'])
def server_authentication():
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    if signature is None or timestamp is None or nonce is None:
        return ""

    value = ''.join(sorted([WECHAT_SERVER_AUTHENTICATION_TOKEN, timestamp, nonce]))
    sha1_value = hashlib.sha1(value.encode('utf-8')).hexdigest()
    if sha1_value != signature:
        app.logger.info("server_authentication sign not match value:" + value + " ; sha1:" + sha1_value)
        return ""

    if request.method == 'POST':
        get_xml_str = request.get_data().decode('utf-8')
        app.logger.info("get xml : [" + get_xml_str + "]")

        dom_tree = xml.dom.minidom.parseString(get_xml_str)
        root = dom_tree.documentElement
        text_tun = root.getElementsByTagName('ToUserName')[0].firstChild.data
        text_fun = root.getElementsByTagName('FromUserName')[0].firstChild.data
        text_ct = root.getElementsByTagName('CreateTime')[0].firstChild.data
        text_mt = root.getElementsByTagName('MsgType')[0].firstChild.data

        ret_doc = xml.dom.minidom.Document()
        element_root = ret_doc.createElement('xml')

        element_to_user_name = ret_doc.createElement('ToUserName')
        text_to_user_name = ret_doc.createCDATASection(text_fun)
        element_to_user_name.appendChild(text_to_user_name)

        element_from_user_name = ret_doc.createElement('FromUserName')
        text_from_user_name = ret_doc.createCDATASection(text_tun)
        element_from_user_name.appendChild(text_from_user_name)

        element_root.appendChild(element_to_user_name)
        element_root.appendChild(element_from_user_name)

        # 暂时全部返回文本消息
        element_create_time = ret_doc.createElement('CreateTime')
        text_create_time = ret_doc.createTextNode(text_ct)
        element_create_time.appendChild(text_create_time)

        element_msg_type = ret_doc.createElement('MsgType')
        text_msg_type = ret_doc.createTextNode("text")
        element_msg_type.appendChild(text_msg_type)

        element_root.appendChild(element_create_time)
        element_root.appendChild(element_msg_type)

        if text_mt == "event":
            text_event = root.getElementsByTagName('Event')[0].firstChild.data
            # 点击微信公众号中的 按钮事件
            if text_event == "CLICK":
                text_ek = root.getElementsByTagName('EventKey')[0].firstChild.data
                # 人工客服 按钮
                if text_ek == "click_custom_service":
                    element_content = ret_doc.createElement('Content')
                    text_content = ret_doc.createTextNode("请发送文字: 人工客服")
                    element_content.appendChild(text_content)

                    element_root.appendChild(element_content)
                else:
                    element_content = ret_doc.createElement('Content')
                    text_content = ret_doc.createTextNode("未知click事件:" + text_ek)
                    element_content.appendChild(text_content)

                    element_root.appendChild(element_content)
            # 关注微信公众号事件
            elif text_event == "subscribe":
                element_content = ret_doc.createElement('Content')
                text_content = ret_doc.createTextNode("感谢关注公众号,请点击按钮进行操作")
                element_content.appendChild(text_content)

                element_root.appendChild(element_content)
            # 公众微信号中的扫描按钮事件
            elif text_event == "scancode_push" or text_event == "scancode_waitmsg":
                input_element_scan_info = root.getElementsByTagName('ScanCodeInfo')[0]
                text_st = input_element_scan_info.getElementsByTagName('ScanType')[0].firstChild.data
                text_sr = input_element_scan_info.getElementsByTagName('ScanResult')[0].firstChild.data
                element_content = ret_doc.createElement('Content')
                text_content = ret_doc.createTextNode("扫描[" + text_st + "]" + "成功[" + text_sr + "],请等待处理")
                element_content.appendChild(text_content)

                element_root.appendChild(element_content)
            # 推送模板 用户接受状态返回
            elif text_event == "TEMPLATESENDJOBFINISH":
                text_msg_id = root.getElementsByTagName('MsgID')[0].firstChild.data
                text_status = root.getElementsByTagName('Status')[0].firstChild.data
                wpm = WechatPushMsg.query.filter_by(wechat_msg_id=text_msg_id).first()
                if wpm:
                    if text_status == "success":
                        wpm.push_flag = "succ"
                    else:
                        wpm.push_flag = "fail"
                        wpm.remark = text_status
                    wpm.save()
            else:
                return ""
        else:
            text_content = root.getElementsByTagName('Content')[0].firstChild.data
            if "人工客服" in text_content:
                # 删除默认的文本节点
                element_root.removeChild(element_msg_type)
                element_msg_type.removeChild(text_msg_type)
                element_msg_type.appendChild(ret_doc.createCDATASection("transfer_customer_service"))

                element_root.appendChild(element_msg_type)

                # 默认无返回数据， 返回一条信息给客户
                WechatCall.send_text_by_openid(text_fun, "正在转人工客服,请稍后...")
            else:
                element_content = ret_doc.createElement('Content')
                text_content = ret_doc.createTextNode("请点击按钮进行操作")
                element_content.appendChild(text_content)

                element_root.appendChild(element_content)

        ret_doc.appendChild(element_root)
        xmlstr = ret_doc.toxml()

        app.logger.info("return xml : [" + xmlstr + "]")
        return xmlstr[22:]
    else:
        # authentication
        return request.args.get("echostr")

    return ""
