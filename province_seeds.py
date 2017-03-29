from application.models import *
fjs = SalesAreaHierarchy(name="福建省", level_grade=3)
db.session.add(fjs)
db.session.commit()
for name in ["泉州市","漳州市","三明市","厦门市","龙岩市","宁德市","南平市","莆田市","福州市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=fjs.id)
    db.session.add(item)
    db.session.commit()

ccs = SalesAreaHierarchy(name="重庆市", level_grade=3)
db.session.add(ccs)
db.session.commit()
for name in ["重庆市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=ccs.id)
    db.session.add(item)
    db.session.commit()

hns = SalesAreaHierarchy(name="河南省", level_grade=3)
db.session.add(hns)
db.session.commit()
for name in ["洛阳市","新乡市","信阳市","三门峡市","平顶山市","漯河市","商丘市","濮阳市","鹤壁市","南阳市","许昌市","安阳市","周口市","焦作市","郑州市","驻马店市","开封市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=hns.id)
    db.session.add(item)
    db.session.commit()

ahs = SalesAreaHierarchy(name="安徽省", level_grade=3)
db.session.add(ahs)
db.session.commit()
for name in ["马鞍山市","亳州市","巢湖市","黄山市","合肥市","阜阳市","蚌埠市","淮北市","六安市","宿州市","芜湖市","宣城市","池州市","铜陵市","淮南市","滁州市","安庆市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=ahs.id)
    db.session.add(item)
    db.session.commit()

scs = SalesAreaHierarchy(name="四川省", level_grade=3)
db.session.add(scs)
db.session.commit()
for name in ["阿坝藏族羌族自治州","达州市","甘孜藏族自治州","巴中市","德阳市","广元市","南充市","绵阳市","自贡市","内江市","雅安市","广安市","凉山彝族自治州","攀枝花市","成都市","乐山市","遂宁市","宜宾市","眉山市","资阳市","泸州市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=scs.id)
    db.session.add(item)
    db.session.commit()

sxs = SalesAreaHierarchy(name="山西省", level_grade=3)
db.session.add(sxs)
db.session.commit()
for name in ["阳泉市","朔州市","晋城市","大同市","太原市","临汾市","长治市","吕梁市","晋中市","运城市","忻州市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=sxs.id)
    db.session.add(item)
    db.session.commit()

gds = SalesAreaHierarchy(name="广东省", level_grade=3)
db.session.add(gds)
db.session.commit()
for name in ["茂名市","清远市","潮州市","梅州市","中山市","佛山市","汕头市","汕尾市","肇庆市","东莞市","云浮市","珠海市","阳江市","韶关市","河源市","惠州市","湛江市","江门市","揭阳市","广州市","深圳市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=gds.id)
    db.session.add(item)
    db.session.commit()

nxs = SalesAreaHierarchy(name="宁夏回族自治区", level_grade=3)
db.session.add(nxs)
db.session.commit()
for name in ["中卫市","石嘴山市","吴忠市","银川市","固原市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=nxs.id)
    db.session.add(item)
    db.session.commit()

hljs = SalesAreaHierarchy(name="黑龙江省", level_grade=3)
db.session.add(hljs)
db.session.commit()
for name in ["大庆市","双鸭山市","七台河市","哈尔滨市","牡丹江市","鸡西市","伊春市","齐齐哈尔市","鹤岗市","黑河市","绥化市","大兴安岭地区","佳木斯市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=hljs.id)
    db.session.add(item)
    db.session.commit()

bjs = SalesAreaHierarchy(name="北京市", level_grade=3)
db.session.add(bjs)
db.session.commit()
for name in ["北京市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=bjs.id)
    db.session.add(item)
    db.session.commit()

gxs = SalesAreaHierarchy(name="广西壮族自治区", level_grade=3)
db.session.add(gxs)
db.session.commit()
for name in ["玉林市","防城港市","崇左市","贺州市","来宾市","钦州市","百色市","贵港市","河池市","柳州市","桂林市","梧州市","南宁市","北海市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=gxs.id)
    db.session.add(item)
    db.session.commit()

nmg = SalesAreaHierarchy(name="内蒙古自治区", level_grade=3)
db.session.add(nmg)
db.session.commit()
for name in ["兴安盟","通辽市","巴彦淖尔市","乌兰察布市","呼伦贝尔市","乌海市","锡林郭勒盟","鄂尔多斯市","阿拉善盟","呼和浩特市","赤峰市","包头市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=nmg.id)
    db.session.add(item)
    db.session.commit()

gzs = SalesAreaHierarchy(name="贵州省", level_grade=3)
db.session.add(gzs)
db.session.commit()
for name in ["遵义市","毕节地区","安顺市","黔南布依族苗族自治州","黔西南布依族苗族自治州","六盘水市","贵阳市","铜仁地区","黔东南苗族侗族自治州"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=gzs.id)
    db.session.add(item)
    db.session.commit()

xjs = SalesAreaHierarchy(name="新疆维吾尔自治区", level_grade=3)
db.session.add(xjs)
db.session.commit()
for name in ["塔城地区","克孜勒苏柯尔克孜自治州","喀什地区","博尔塔拉蒙古自治州","阿克苏地区","阿勒泰地区","克拉玛依市","乌鲁木齐市","吐鲁番地区","哈密地区","伊犁哈萨克自治州","和田地区","昌吉回族自治州","巴音郭楞蒙古自治州"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=xjs.id)
    db.session.add(item)
    db.session.commit()

zjs = SalesAreaHierarchy(name="浙江省", level_grade=3)
db.session.add(zjs)
db.session.commit()
for name in ["杭州市","宁波市","温州市","绍兴市","湖州市","舟山市","金华市","衢州市","嘉兴市","台州市","丽水市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=zjs.id)
    db.session.add(item)
    db.session.commit()

xgq = SalesAreaHierarchy(name="香港特别行政区", level_grade=3)
db.session.add(xgq)
db.session.commit()
for name in ["香港"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=xgq.id)
    db.session.add(item)
    db.session.commit()

xzq = SalesAreaHierarchy(name="西藏自治区", level_grade=3)
db.session.add(xzq)
db.session.commit()
for name in ["那曲地区","林芝地区","日喀则地区","昌都地区","山南地区","阿里地区","拉萨市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=xzq.id)
    db.session.add(item)
    db.session.commit()

shs = SalesAreaHierarchy(name="上海市", level_grade=3)
db.session.add(shs)
db.session.commit()
for name in ["上海市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=shs.id)
    db.session.add(item)
    db.session.commit()

hbs = SalesAreaHierarchy(name="河北省", level_grade=3)
db.session.add(hbs)
db.session.commit()
for name in ["唐山市","保定市","张家口市","秦皇岛市","承德市","邢台市","衡水市","石家庄市","沧州市","廊坊市","邯郸市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=hbs.id)
    db.session.add(item)
    db.session.commit()

hbs_2 = SalesAreaHierarchy(name="湖北省", level_grade=3)
db.session.add(hbs_2)
db.session.commit()
for name in ["荆门市","襄阳市","十堰市","孝感市","咸宁市","随州市","黄石市","鄂州市","武汉市","恩施土家族苗族自治州","宜昌市","荆州市","黄冈市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=hbs_2.id)
    db.session.add(item)
    db.session.commit()

gss = SalesAreaHierarchy(name="甘肃省", level_grade=3)
db.session.add(gss)
db.session.commit()
for name in ["陇南市","平凉市","张掖市","庆阳市","武威市","天水市","嘉峪关市","临夏回族自治州","白银市","兰州市","定西市","甘南藏族自治州","酒泉市","金昌市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=gss.id)
    db.session.add(item)
    db.session.commit()

jsx = SalesAreaHierarchy(name="江苏省", level_grade=3)
db.session.add(jsx)
db.session.commit()
for name in ["南京市","南通市","连云港市","扬州市","镇江市","苏州市","徐州市","无锡市","常州市","淮安市","泰州市","盐城市","宿迁市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=jsx.id)
    db.session.add(item)
    db.session.commit()

tjs = SalesAreaHierarchy(name="天津市", level_grade=3)
db.session.add(tjs)
db.session.commit()
for name in ["天津市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=tjs.id)
    db.session.add(item)
    db.session.commit()

hns_2 = SalesAreaHierarchy(name="湖南省", level_grade=3)
db.session.add(hns_2)
db.session.commit()
for name in ["株洲市","长沙市","湘潭市","常德市","岳阳市","怀化市","张家界市","邵阳市","娄底市","湘西土家族苗族自治州","永州市","益阳市","衡阳市","郴州市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=hns_2.id)
    db.session.add(item)
    db.session.commit()

sdx = SalesAreaHierarchy(name="山东省", level_grade=3)
db.session.add(sdx)
db.session.commit()
for name in ["潍坊市","烟台市","滨州市","莱芜市","淄博市","威海市","济宁市","聊城市","日照市","临沂市","青岛市","菏泽市","枣庄市","泰安市","德州市","东营市","济南市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=sdx.id)
    db.session.add(item)
    db.session.commit()

hns_3 = SalesAreaHierarchy(name="海南省", level_grade=3)
db.session.add(hns_3)
db.session.commit()
for name in ["海口市","三亚市","三沙市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=hns_3.id)
    db.session.add(item)
    db.session.commit()

sxs_2 = SalesAreaHierarchy(name="陕西省", level_grade=3)
db.session.add(sxs_2)
db.session.commit()
for name in ["安康市","延安市","商洛市","渭南市","铜川市","宝鸡市","咸阳市","榆林市","西安市","汉中市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=sxs_2.id)
    db.session.add(item)
    db.session.commit()

jlx = SalesAreaHierarchy(name="吉林省", level_grade=3)
db.session.add(jlx)
db.session.commit()
for name in ["白山市","松原市","白城市","辽源市","四平市","长春市","吉林市","延边朝鲜族自治州","通化市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=jlx.id)
    db.session.add(item)
    db.session.commit()

qhs = SalesAreaHierarchy(name="青海省", level_grade=3)
db.session.add(qhs)
db.session.commit()
for name in ["海北藏族自治州","黄南藏族自治州","玉树藏族自治州","海西蒙古族藏族自治州","果洛藏族自治州","西宁市","海东地区","海南藏族自治州"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=qhs.id)
    db.session.add(item)
    db.session.commit()

lns = SalesAreaHierarchy(name="辽宁省", level_grade=3)
db.session.add(lns)
db.session.commit()
for name in ["沈阳市","朝阳市","大连市","丹东市","抚顺市","鞍山市","盘锦市","铁岭市","辽阳市","锦州市","本溪市","葫芦岛市","阜新市","营口市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=lns.id)
    db.session.add(item)
    db.session.commit()

jxs = SalesAreaHierarchy(name="江西省", level_grade=3)
db.session.add(jxs)
db.session.commit()
for name in ["鹰潭市","南昌市","宜春市","萍乡市","赣州市","吉安市","上饶市","抚州市","新余市","九江市","景德镇市"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=jxs.id)
    db.session.add(item)
    db.session.commit()

yns = SalesAreaHierarchy(name="云南省", level_grade=3)
db.session.add(yns)
db.session.commit()
for name in ["玉溪市","迪庆藏族自治州","保山市","曲靖市","红河哈尼族彝族自治州","普洱市","大理白族自治州","怒江傈僳族自治州","临沧市","德宏傣族景颇族自治州","昆明市","丽江市","西双版纳傣族自治州","昭通市","文山壮族苗族自治州","楚雄彝族自治州"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=yns.id)
    db.session.add(item)
    db.session.commit()

tws = SalesAreaHierarchy(name="台湾省", level_grade=3)
db.session.add(tws)
db.session.commit()
for name in ["新北市","台北市","台中市","台南市","高雄市","基隆市","新竹市","嘉义市","桃园县","新竹县","苗栗县","彰化县","南投县","云林县","嘉义县","屏东县","宜兰县","花莲县","台东县","澎湖县","金门县","连江县"]:
    item = SalesAreaHierarchy(name=name, level_grade=4, parent_id=tws.id)
    db.session.add(item)
    db.session.commit()

db.session.commit()
