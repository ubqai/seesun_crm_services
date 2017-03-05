from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .. import app, db
from .models import *

import hashlib
from xml.dom.minidom import parse 
import xml.dom.minidom 

wechat = Blueprint('wechat', __name__, template_folder = 'templates')

@wechat.route('/mobile/verification', methods=['GET', 'POST'])
def mobile_verification():
    wechat_info = WechatAccessToken.getJsApiSign(request.url)
    if request.method == 'POST':
        app.logger.info("wechat.mobile_verification: [%s]" , request.form.get("text-verification"))
        flash('校验成功', 'success')
        return render_template('wechat/mobile_verification.html',wechat_info=wechat_info)
    else:
        return render_template('wechat/mobile_verification.html',wechat_info=wechat_info)


@wechat.route("/server/authentication", methods=['GET', 'POST'])
def server_authentication():
    signature=request.args.get("signature")
    timestamp=request.args.get("timestamp")
    nonce=request.args.get("nonce")

    if signature==None or timestamp==None or nonce==None:
        return ""

    value=''.join(sorted([WECHAT_SERVER_AUTHENTICATION_TOKEN,timestamp,nonce]))
    sha1_value=hashlib.sha1(value.encode('utf-8')).hexdigest()
    if sha1_value!=signature:
        app.logger.info("server_authentication sign not match value:"+value+" ; sha1:"+sha1_value)
        return ""

    if request.method == 'POST':
        get_xml_str=request.get_data().decode('utf-8')
        app.logger.info("get xml : [" + get_xml_str+"]")
        # DOMTree = xml.dom.minidom.parseString(str(request.get_data())
        # root.getElementsByTagName('ToUserName')[0].firstChild.data
        # root.getElementsByTagName('CreateTime')[0].firstChild.data

        DOMTree = xml.dom.minidom.parseString(get_xml_str)
        root=DOMTree.documentElement
        text_tun=root.getElementsByTagName('ToUserName')[0].firstChild.data
        text_fun=root.getElementsByTagName('FromUserName')[0].firstChild.data
        text_ct=root.getElementsByTagName('CreateTime')[0].firstChild.data
        text_mt=root.getElementsByTagName('MsgType')[0].firstChild.data

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

        #暂时全部返回文本消息
        element_create_time = ret_doc.createElement('CreateTime') 
        text_create_time = ret_doc.createTextNode(text_ct)
        element_create_time.appendChild(text_create_time)

        element_msg_type = ret_doc.createElement('MsgType') 
        text_msg_type = ret_doc.createTextNode("text")
        element_msg_type.appendChild(text_msg_type)

        element_root.appendChild(element_create_time)
        element_root.appendChild(element_msg_type)

        if text_mt=="event":
            text_event=root.getElementsByTagName('Event')[0].firstChild.data
            text_ek=root.getElementsByTagName('EventKey')[0].firstChild.data
            if text_event=="CLICK":
                if text_ek=="click_bind_user":
                    element_content = ret_doc.createElement('Content') 
                    text_content = ret_doc.createTextNode("功能尚在开发")
                    element_content.appendChild(text_content)

                    element_root.appendChild(element_content)
                else:
                    element_content = ret_doc.createElement('Content') 
                    text_content = ret_doc.createTextNode("未知click事件:"+text_ek)
                    element_content.appendChild(text_content)

                    element_root.appendChild(element_content)        
            elif text_event=="subscribe":
                element_content = ret_doc.createElement('Content') 
                text_content = ret_doc.createTextNode("感谢关注公众号,请点击按钮进行操作")
                element_content.appendChild(text_content)

                element_root.appendChild(element_content)
            elif text_event=="scancode_push" or text_event=="scancode_waitmsg":
                input_element_scan_info=root.getElementsByTagName('ScanCodeInfo')[0]
                text_st=input_element_scan_info.getElementsByTagName('ScanType')[0].firstChild.data
                text_sr=input_element_scan_info.getElementsByTagName('ScanResult')[0].firstChild.data
                element_content = ret_doc.createElement('Content') 
                text_content = ret_doc.createTextNode("扫描["+text_st+"]"+"成功["+text_sr+"],请等待处理")
                element_content.appendChild(text_content)

                element_root.appendChild(element_content)
            else:
                return ""
        else:
            element_content = ret_doc.createElement('Content') 
            text_content = ret_doc.createTextNode("请点击按钮进行操作")
            element_content.appendChild(text_content)

            element_root.appendChild(element_content)

        ret_doc.appendChild(element_root)
        xmlstr= ret_doc.toxml()

        app.logger.info("return xml : [" + xmlstr+"]")
        return xmlstr[22:len(xmlstr)]
    else:
        #authentication
        return request.args.get("echostr")

    return ""