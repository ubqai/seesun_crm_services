# -*- coding: utf-8 -*-
import datetime
import requests
import json
from .. import db

WECHAT_SERVER_AUTHENTICATION_TOKEN="AUTH_TOKEN_135"
WECHAT_APPID="wx05617a940b6ca40e"
WECHAT_APPSECRET="a0f13258cf8e959970260b24a9dea2de"

#from application.wechat.models import *
#from application.wechat.models import WechatAccessToken
class WechatAccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500) , nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    expires_in = db.Column(db.Integer)
    expires_at = db.Column(db.DateTime,nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    use_flag = db.Column(db.Boolean,default=True)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def applyAccessToken(cls):
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (WECHAT_APPID, WECHAT_APPSECRET)
            response = requests.get(url)
            if response.status_code != 200:
                return "get failure"

            res_json=response.json()

            if res_json.get("errcode")!=None:
                return "get failure :" + res_json.get("errmsg")

            wat=WechatAccessToken(access_token=res_json.get("access_token"),expires_in=res_json.get("expires_in"),use_flag=True)
            wat.created_at = datetime.datetime.now()
            wat.expires_at = wat.created_at + datetime.timedelta(seconds=wat.expires_in)

            wat.save()

            return wat

    @classmethod
    def getToken(cls):
        wat=WechatAccessToken.query.filter_by(use_flag=True).first()
        if wat==None:
            wat=applyAccessToken()
        if wat==None or wat.access_token==None:
            raise BaseException("wechat: no access_token can use !!")

        return wat.access_token



class WechatCall:
    @classmethod
    def createMenu(cls):
        url="https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % (WechatAccessToken.getToken())
        crm_services_url="http://118.178.185.40"
        headers = {'content-type': 'application/json'}
        post_params=json.dumps({
            "button":[
                {
                    "type":"click",
                    "name":"用户绑定".encode("utf-8").decode("latin1"),
                    "key":"click_bind_user"
                },
                {
                    "type":"view",
                    "name":"服务站".encode("utf-8").decode("latin1"),
                    "url": crm_services_url
                }
            ]   
        }, ensure_ascii=False)

        response = requests.post(url, data=post_params, headers=headers)
        if response.status_code != 200:
            return "get failure"

        res_json=response.json()

        if res_json.get("errcode")!=0:
            raise BaseException("wechat: create menu failure [%s] - [%s]" % (post_params,res_json))