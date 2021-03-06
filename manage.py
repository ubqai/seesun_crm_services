# -*- coding: utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from application import app, db
from application.models import *
from application.wechat.models import *
from application.web_access_log.models import WebAccessLog
import application.views

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, Content=Content, ContentCategory=ContentCategory,
                ContentClassification=ContentClassification,
                ContentClassificationOption=ContentClassificationOption,
                Material=Material, MaterialApplication=MaterialApplication,
                MaterialApplicationContent=MaterialApplicationContent, DesignApplication=DesignApplication,
                TrackingInfo=TrackingInfo, TrackingInfoDetail=TrackingInfoDetail,
                LogisticsCompanyInfo=LogisticsCompanyInfo,
                Order=Order, OrderContent=OrderContent, Contract=Contract,
                User=User, UserInfo=UserInfo, Resource=Resource, SalesAreaHierarchy=SalesAreaHierarchy,
                DepartmentHierarchy=DepartmentHierarchy, UserAndSaleArea=UserAndSaleArea,
                WechatAccessToken=WechatAccessToken, WechatCall=WechatCall, WechatUserInfo=WechatUserInfo,
                WechatPushMsg=WechatPushMsg,
                ProjectReport=ProjectReport, WebAccessLog=WebAccessLog, ShareInventory=ShareInventory,
                WebpageDescribe=WebpageDescribe, AuthorityOperation=AuthorityOperation)


manager.add_command("shell", Shell(make_context=make_shell_context))


# 微信token定时检测任务
@manager.command
def cron_wechat_token():
    WechatAccessToken.cron_create_token()


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
