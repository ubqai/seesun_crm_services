from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .. import app, db
import hashlib

wechat = Blueprint('wechat', __name__, template_folder = 'templates')

SERVER_AUTHENTICATION_TOKEN="AUTH_TOKEN_135"

@wechat.route('/index/test')
def test():
    return render_template('wechat/test.html')

@wechat.route("/server/authentication")
def server_authentication():
    signature=request.args.get("signature")
    timestamp=request.args.get("timestamp")
    nonce=request.args.get("nonce")
    echostr=request.args.get("echostr")

    app.logger.info("into server_authentication [%s],[%s],[%s],[%s]" % (signature,timestamp,nonce,echostr))
    value=''.join(sorted([SERVER_AUTHENTICATION_TOKEN,timestamp,nonce]))
    sha1_value=hashlib.sha1(value.encode('utf-8')).hexdigest()
    app.logger.info("value:"+value+" ; sha1:"+sha1_value)

    if sha1_value==signature:
        return echostr

    return "error"