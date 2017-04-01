from application.models import *
zg = SalesAreaHierarchy(name="中国", level_grade=1)
db.session.add(zg)
db.session.commit()

for name in ["华东区", "华南区", "华中区", "华北区", "东北区", "西北区", "西南区"]:
    item = SalesAreaHierarchy(name=name, level_grade=2, parent_id=zg.id)
    db.session.add(item)
    db.session.commit()

