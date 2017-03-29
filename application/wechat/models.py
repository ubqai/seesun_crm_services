# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
import random
import string
import time
import urllib

import requests

from .. import db, app

WECHAT_SERVER_AUTHENTICATION_TOKEN = "AUTH_TOKEN_135"
WECHAT_APPID = "wx05617a940b6ca40e"
WECHAT_APPSECRET = "a0f13258cf8e959970260b24a9dea2de"

WECHAT_TEST_APPID = "wx7b03a1827461854d"
WECHAT_TEST_APPSECRET = "3c48165926a74837bfc6c61442925943"

TEST_MODE = app.config['WECHAT_TEST_MODE']
HOOK_URL = app.config['WECHAT_HOOK_URL']

TEMPLATE_DESC = {
    "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0": "订单状态提醒"
}


class DbBaseOperation(object):
    def save(self):
        # 增加rollback防止一个异常导致后续SQL不可使用
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


# 微信帐号与经销商用户绑定表
class WechatUserInfo(db.Model, DbBaseOperation):
    id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column(db.String(200), nullable=False)  # wechat - openid
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    active_time = db.Column(db.DateTime, default=datetime.datetime.now)
    push_msgs = db.relationship('WechatPushMsg', backref='wechat_user_info', lazy='dynamic')


# 推送微信的各种消息记录
class WechatPushMsg(db.Model, DbBaseOperation):
    id = db.Column(db.Integer, primary_key=True)
    wechat_msg_id = db.Column(db.String(100))  # 微信返回的msgId等
    wechat_user_info_id = db.Column(db.Integer, db.ForeignKey('wechat_user_info.id'))
    push_type = db.Column(db.String(20), nullable=False)  # 推送类型 - text,template等
    push_info = db.Column(db.JSON, default={})  # 推送内容
    push_time = db.Column(db.DateTime, default=datetime.datetime.now)  # 推送时间
    push_flag = db.Column(db.String(10))  # 推送是否成功
    push_remark = db.Column(db.String(200))  # 推送失败原因等
    push_times = db.Column(db.Integer, default=1)  # 推送次数


# from application.wechat.models import *
# from application.wechat.models import WechatAccessToken
# 存放微信使用的各种Token,存在过期时间
class WechatAccessToken(db.Model, DbBaseOperation):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    expires_in = db.Column(db.Integer)
    expires_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    use_flag = db.Column(db.Boolean, default=True)
    appid = db.Column(db.String(100), nullable=False)
    token_type = db.Column(db.String(50), nullable=False)

    TOKEN_TYPE_HASH = {
        "access_token": "通用接口token",
        "jsapi_ticket": "网页JS认证token"
    }

    # 服务器定时任务,创建10条可用token
    @classmethod
    def cron_create_token(cls, max_count=10, is_test=TEST_MODE):
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        for token_type in cls.TOKEN_TYPE_HASH.keys():
            WechatAccessToken.check_token_by_type(token_type, is_test)
            can_use_count = WechatAccessToken.query.filter(
                WechatAccessToken.use_flag == True, WechatAccessToken.appid == use_appid,
                WechatAccessToken.token_type == token_type).count()
            for i in range(max_count - can_use_count):
                if token_type == "access_token":
                    cls.apply_access_token()
                elif token_type == "jsapi_ticket":
                    cls.apply_jsap_ticket()
            print("[%s] can_use_count = %d and apply_count = %d"
                  % (token_type, can_use_count, max_count - can_use_count))

    # 检查token是否超过有效时间,修改为不可使用
    @classmethod
    def check_token_by_type(cls, token_type, is_test=TEST_MODE):
        print("checkAccessToken is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        valid_count = 0
        threshold_time = datetime.datetime.now() - datetime.timedelta(seconds=600)
        print("checkAccessToken threshold_time : [%s]" % threshold_time)
        wats = WechatAccessToken.query.filter(WechatAccessToken.expires_at < threshold_time,
                                              WechatAccessToken.use_flag == True, WechatAccessToken.appid == use_appid,
                                              WechatAccessToken.token_type == token_type).all()
        for wat in wats:
            print("WechatAccessToken update Invalid : [%s],[%s]" % (wat.access_token, wat.expires_at))
            wat.use_flag = "N"
            wat.save()
            valid_count += 1

        # 返回校验更新的数量
        return valid_count

    # 申请access_token - 基本推送接口使用
    @classmethod
    def apply_access_token(cls, is_test=TEST_MODE):
        print("apply_access_token is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
            use_appsecret = WECHAT_APPSECRET
        else:
            use_appid = WECHAT_TEST_APPID
            use_appsecret = WECHAT_TEST_APPSECRET

        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
            use_appid, use_appsecret)
        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode") is not None:
            return "get failure :" + res_json.get("errmsg")

        wat = WechatAccessToken(access_token=res_json.get("access_token"), expires_in=res_json.get("expires_in"),
                                use_flag=True)
        wat.created_at = datetime.datetime.now()
        wat.expires_at = wat.created_at + datetime.timedelta(seconds=wat.expires_in)
        wat.appid = use_appid
        wat.token_type = "access_token"

        wat.save()

        return wat

    # 申请jsapi_ticket - js sdk 使用
    @classmethod
    def apply_jsap_ticket(cls, is_test=TEST_MODE):
        print("apply_jsap_ticket is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))
        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode") != 0:
            return "get failure :" + res_json.get("errmsg")

        wat = WechatAccessToken(access_token=res_json.get("ticket"), expires_in=res_json.get("expires_in"),
                                use_flag=True)
        wat.created_at = datetime.datetime.now()
        wat.expires_at = wat.created_at + datetime.timedelta(seconds=wat.expires_in)
        wat.appid = use_appid
        wat.token_type = "jsapi_ticket"

        wat.save()

        return wat

    # 获取可用token值
    @classmethod
    def get_token_by_type(cls, token_type, is_test=TEST_MODE):
        print("get_token_by_type is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        WechatAccessToken.check_token_by_type(token_type, is_test)

        wat = WechatAccessToken.query.filter_by(use_flag=True, appid=use_appid, token_type=token_type).order_by(
            "random()").first()
        if wat is None:
            if token_type == "access_token":
                wat = WechatAccessToken.apply_access_token(is_test)
            elif token_type == "jsapi_ticket":
                wat = WechatAccessToken.apply_jsap_ticket(is_test)
            else:
                pass
        if wat is None or wat.access_token is None:
            raise BaseException("wechat: no access_token can use !!")

        print("[%s] info [%s] , appid[%s]" % (token_type, wat.access_token, wat.appid))
        return wat.access_token

    # jssdk签名计算
    @classmethod
    def get_js_api_sign(cls, url, is_test=TEST_MODE):
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        # 获取随即字符串
        sign_params = {
            "jsapi_ticket": WechatAccessToken.get_token_by_type("jsapi_ticket", is_test),
            "noncestr": ''.join(random.sample(string.ascii_letters + string.digits, 16)),
            "timestamp": str(int(time.time())),
            "url": url
        }

        sign_array = []
        for key in sorted(sign_params.keys()):
            sign_array.append(key + "=" + str(sign_params[key]))
        sign_value = '&'.join(sign_array)

        sign_params['sign'] = hashlib.sha1(sign_value.encode('utf-8')).hexdigest()
        sign_params['appid'] = use_appid
        sign_params['is_test'] = is_test

        print("getJsApiSign [%s] --> [%s]" % (sign_value, sign_params['sign']))
        return sign_params


# 后端调用微信服务类
class WechatCall:
    # 创建自定义菜单
    @classmethod
    def create_menu(cls, is_test=TEST_MODE):
        print("create_menu is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))
        crm_services_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" + \
                           "appid=" + use_appid + \
                           "&redirect_uri=" + urllib.parse.quote_plus(HOOK_URL + "/mobile/user/login") + \
                           "&response_type=code&scope=snsapi_base&state=wechat_user_binding#wechat_redirect"

        crm_user_binding_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" + \
                               "appid=" + use_appid + \
                               "&redirect_uri=" + urllib.parse.quote_plus(HOOK_URL + "/wechat/mobile/user_binding") + \
                               "&response_type=code&scope=snsapi_base&state=wechat_user_binding#wechat_redirect"
        app.logger.info("crm_user_binding_url [%s] \n crm_services_url [%s]" % (crm_user_binding_url, crm_services_url))

        headers = {'content-type': 'application/json'}
        post_params = json.dumps({
            "button": [
                {
                    "type": "view",
                    "name": "用户绑定".encode("utf-8").decode("latin1"),
                    "url": crm_user_binding_url
                },
                {
                    "name": "相关服务".encode("utf-8").decode("latin1"),
                    "sub_button": [
                        {
                            "type": "scancode_waitmsg",
                            "name": "检验真伪".encode("utf-8").decode("latin1"),
                            "key": "click_scan_wait"
                        },
                        {
                            "type": "click",
                            "name": "人工客服".encode("utf-8").decode("latin1"),
                            "key": "click_custom_service"
                        },
                        {
                            "type": "view",
                            "name": "服务站".encode("utf-8").decode("latin1"),
                            "url": crm_services_url
                        }
                    ]
                }
            ]
        }, ensure_ascii=False)

        response = requests.post(url, data=post_params, headers=headers)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode") != 0:
            raise BaseException("wechat: create menu failure [%s] - [%s]" % (post_params, res_json))

        return res_json.get("errmsg")

    # 删除自定义菜单
    @classmethod
    def delete_menu(cls, is_test=TEST_MODE):
        print("delete_menu is_test: %s" % is_test)

        url = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))
        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode") != 0:
            return "get failure :" + res_json.get("errmsg")

    # 获取openId
    @classmethod
    def get_open_id_by_code(cls, code, is_test=TEST_MODE):
        print("get_open_id_by_code is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
            use_appsecret = WECHAT_APPSECRET
        else:
            use_appid = WECHAT_TEST_APPID
            use_appsecret = WECHAT_TEST_APPSECRET

        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" \
              % (use_appid, use_appsecret, code)
        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode", 0) != 0:
            raise ValueError("get failure :" + res_json.get("errmsg", "unknown errmsg"))

        return res_json.get("openid", "")

    # 推送消息 - openid
    @classmethod
    def send_text_by_openid(cls, open_id, msg, is_test=TEST_MODE):
        if not open_id or not msg:
            raise ValueError("user_id and msg can not null")

        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))

        try:
            headers = {'content-type': 'application/json'}
            post_params = json.dumps({
                "touser": open_id,
                "msgtype": "text",
                "text": {
                    "content": msg.encode("utf-8").decode("latin1"),
                }
            }, ensure_ascii=False)

            app.logger.info("send_text_to_user params : [" + post_params + "]")
            response = requests.post(url, data=post_params, headers=headers)

            if response.status_code != 200:
                raise ConnectionError("get url failure %d" % response.status_code)

            res_json = response.json()

            if res_json.get("errcode", 0) != 0:
                app.logger.info(res_json)
                raise ValueError(res_json.get("errcode"))

        except Exception as e:
            app.logger.info("send_text_to_user failure %s" % e)
        finally:
            wpm = WechatPushMsg(
                push_type="text",
                push_info=post_params
            )

            if res_json:
                if res_json.get("errcode", 0) != 0:
                    wpm.push_flag = "fail"
                    wpm.remark = res_json.get("errcode") + " [" + res_json.get("errmsg", "") + "]"
                else:
                    wpm.push_flag = "succ"
                    wpm.wechat_msg_id = res_json.get("msgid", "")
            else:
                wpm.push_flag = "push_fail"
                wpm.remark = "请求返回异常"

        # 返回待记录数据由调用方处理是否插入
        return wpm

    # 推送消息 - 已绑定用户
    @classmethod
    def send_text_to_user(cls, user_id, msg, is_test=TEST_MODE):
        if not user_id or not msg:
            raise ValueError("user_id and msg can not null")

        for wui in WechatUserInfo.query.filter_by(user_id=user_id).all():
            wpm = cls.send_text_by_openid(wui.open_id, msg, is_test)
            wpm.wechat_user_info_id = wui.id
            wpm.save()

    # 推送消息模板
    @classmethod
    def send_template_to_user(cls, user_id, template_id, params_hash, is_test=TEST_MODE):
        if not user_id or not template_id:
            raise ValueError("user_id and template_id can not null")

        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))

        for wui in WechatUserInfo.query.filter_by(user_id=user_id).all():
            try:
                headers = {'content-type': 'application/json'}

                post_params = {
                    "touser": wui.open_id,
                    "template_id": template_id,
                    "topcolor": "#FF0000",
                    # "url": "",   # 模板跳转地址
                    "data": {}
                }
                for key_var in params_hash.keys():
                    value = params_hash[key_var].get("value", "").encode("utf-8").decode("latin1")
                    color = params_hash[key_var].get("color", "#173177")
                    post_params["data"][key_var] = {
                        "value": value,
                        "color": color
                    }

                json_params = json.dumps(post_params, ensure_ascii=False)

                app.logger.info("send_template_to_user params : [" + json_params + "]")
                response = requests.post(url, data=json_params, headers=headers)

                if response.status_code != 200:
                    raise ConnectionError("get url failure %d" % response.status_code)

                res_json = response.json()

                if res_json.get("errcode", 0) != 0:
                    app.logger.info(res_json)
                    raise ValueError(res_json.get("errcode"))
            except Exception as e:
                app.logger.info("send_template_to_user failure %s" % e)
            finally:
                wpm = WechatPushMsg(
                    wechat_user_info_id=wui.id,
                    push_type="template",
                    push_info=json_params
                )

                if res_json:
                    if res_json.get("errcode", 0) != 0:
                        wpm.push_flag = "push_fail"
                        wpm.remark = res_json.get("errcode") + " [" + res_json.get("errmsg", "") + "]"
                    else:
                        wpm.push_flag = "init"
                        wpm.wechat_msg_id = res_json.get("msgid", "")
                else:
                    wpm.push_flag = "push_fail"
                    wpm.remark = "请求返回异常"

                wpm.save()

    # 获取所有客服基本信息
    @classmethod
    def get_kf_list(cls, is_test=TEST_MODE):
        url = "https://api.weixin.qq.com/cgi-bin/customservice/getkflist?access_token=%s" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))

        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode", 0) != 0:
            raise ValueError("get failure :" + res_json.get("errmsg", "unknown errmsg"))
        # print("kf list: ", res_json)
        for kf_hash in res_json['kf_list']:
            print("客服帐号[%s]:微信号[%s],昵称[%s]" % (kf_hash['kf_account'], kf_hash['kf_wx'], kf_hash['kf_nick']))

    # 获取客服信息--是否在线,接待人数
    @classmethod
    def get_kf_list_online(cls, is_test=TEST_MODE):
        url = "https://api.weixin.qq.com/cgi-bin/customservice/getonlinekflist?access_token=%s" % (
            WechatAccessToken.get_token_by_type("access_token", is_test))

        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode", 0) != 0:
            raise ValueError("get failure :" + res_json.get("errmsg", "unknown errmsg"))
        # print("kf list: ", res_json)
        for kf_hash in res_json['kf_online_list']:
            if kf_hash['status'] == 1:
                status = "在线"
            else:
                status = "离线"
            print("客服帐号[%s]:是否在线[%s],正接待会话数[%d]" % (kf_hash['kf_account'], status, kf_hash['accepted_case']))
