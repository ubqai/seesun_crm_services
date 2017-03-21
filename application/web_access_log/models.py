import datetime
from .. import db


class WebAccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_path = db.Column(db.String(200))
    user_id = db.Column(db.Integer)
    remote_addr = db.Column(db.String(15))
    user_agent = db.Column(db.String(500))
    platform = db.Column(db.String(20))
    browser = db.Column(db.String(20))
    version = db.Column(db.String(20))
    language = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return """
        WebAccessLog(id: {id}, request_path: {request_path}, user_id: {user_id}, remote_addr: {remote_addr},
        user_agent: {user_agent})
        """.format(id=self.id, request_path=self.request_path, user_id=self.user_id, remote_addr=self.remote_addr,
                   user_agent=self.user_agent)

    @classmethod
    def take_record(cls, request, current_user):
        return cls(request_path=request.path,
                   user_id=current_user.id,
                   remote_addr=request.access_route[0],
                   user_agent=request.user_agent.string,
                   platform=request.user_agent.platform,
                   browser=request.user_agent.browser,
                   version=request.user_agent.version,
                   language=request.user_agent.language)
