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


class WechatUserInfo(db.Model, DbBaseOperation):
    id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column(db.String(200), nullable=False)  # wechat - openid
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    active_time = db.Column(db.DateTime, default=datetime.datetime.now)


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

    # 检查token是否超过有效时间,修改为不可使用
    @classmethod
    def checkTokenByType(cls, token_type, is_test=TEST_MODE):
        print("checkAccessToken is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        threshold_time = datetime.datetime.now() - datetime.timedelta(seconds=600)
        print("checkAccessToken threshold_time : [%s]" % threshold_time)
        wats = WechatAccessToken.query.filter(WechatAccessToken.expires_at < threshold_time,
                                              WechatAccessToken.use_flag == True, WechatAccessToken.appid == use_appid,
                                              WechatAccessToken.token_type == token_type).all()
        for wat in wats:
            print("WechatAccessToken update Invalid : [%s],[%s]" % (wat.access_token, wat.expires_at))
            wat.use_flag = "N"
            wat.save()

        return ""

    # 申请access_token - 基本推送接口使用
    @classmethod
    def applyAccessToken(cls, is_test=TEST_MODE):
        print("applyAccessToken is_test: %s" % is_test)
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
    def applyJsapTicket(cls, is_test=TEST_MODE):
        print("applyJsapTicket is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % (
            WechatAccessToken.getTokenByType("access_token", is_test))
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
    def getTokenByType(cls, token_type, is_test=TEST_MODE):
        print("getTokenByType is_test: %s" % is_test)
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        WechatAccessToken.checkTokenByType(token_type, is_test)

        wat = WechatAccessToken.query.filter_by(use_flag=True, appid=use_appid, token_type=token_type).first()
        if wat is None:
            if token_type == "access_token":
                wat = WechatAccessToken.applyAccessToken(is_test)
            elif token_type == "jsapi_ticket":
                wat = WechatAccessToken.applyJsapTicket(is_test)
            else:
                pass
        if wat is None or wat.access_token is None:
            raise BaseException("wechat: no access_token can use !!")

        print("[%s] info [%s] , appid[%s]" % (token_type, wat.access_token, wat.appid))
        return wat.access_token

    # jssdk签名计算
    @classmethod
    def getJsApiSign(cls, url, is_test=TEST_MODE):
        if is_test is False:
            use_appid = WECHAT_APPID
        else:
            use_appid = WECHAT_TEST_APPID

        # 获取随即字符串
        sign_params = {
            "jsapi_ticket": WechatAccessToken.getTokenByType("jsapi_ticket", is_test),
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
            WechatAccessToken.getTokenByType("access_token", is_test))
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
            WechatAccessToken.getTokenByType("access_token", is_test))
        response = requests.get(url)
        if response.status_code != 200:
            return "get failure"

        res_json = response.json()

        if res_json.get("errcode") != 0:
            return "get failure :" + res_json.get("errmsg")

    # 获取openId
    @classmethod
    def getOpenIdByCode(cls, code, is_test=TEST_MODE):
        print("getOpenIdByCode is_test: %s" % is_test)
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

    # 推送消息
    @classmethod
    def send_text_to_user(cls, user_id, msg, is_test=TEST_MODE):
        if not user_id or not msg:
            raise ValueError("user_id and msg can not null")

        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % (
            WechatAccessToken.getTokenByType("access_token", is_test))

        for wui in WechatUserInfo.query.filter_by(user_id=user_id).all():
            try:
                headers = {'content-type': 'application/json'}
                post_params = json.dumps({
                    "touser": wui.open_id,
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

    # 推送消息模板
    # WechatCall.send_template_to_user("op2_o1GdwA5SGFaVxqXnKpYHs73k",
    #   "lW5jdqbUIcAwTF5IVy8iBzZM-TXMn1hVf9qWOtKZWb0",
    #   )
    @classmethod
    def send_template_to_user(cls, user_id, template_id, params_hash, is_test=TEST_MODE):
        if not user_id or not template_id:
            raise ValueError("user_id and template_id can not null")

        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % (
            WechatAccessToken.getTokenByType("access_token", is_test))

        for wui in WechatUserInfo.query.filter_by(user_id=user_id).all():
            try:
                headers = {'content-type': 'application/json'}

                post_params = {
                    "touser": wui.open_id,
                    "template_id": template_id,
                    "topcolor": "#FF0000",
                    # "url": "",   # 模板跳转地址
                    "data": {params_hash.encode("utf-8").decode("latin1")}
                }
                # for key_var in params_hash.keys():
                #     value = params_hash[key_var].get("value", "").encode("utf-8").decode("latin1")
                #     color = params_hash[key_var].get("color", "#173177")
                #     post_params["data"][key_var] = {
                #         "value": value,
                #         "color": color
                #     }

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
