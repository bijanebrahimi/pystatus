# from python
from datetime import datetime
from random import choice
from hashlib import md5

# from flask
from flask.ext.sqlalchemy import SQLAlchemy

# from friendfile
from pystatus.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=True)
    public_key = db.Column(db.String(255), nullable=True)
    created = db.Column(db.DateTime(),
                        default=datetime.now)
    modified = db.Column(db.DateTime(),
                         default=datetime.now,
                         onupdate=datetime.now)

    @property
    def uri(self):
        # BUG: should be absolute path
        return '/user/%d' % self.id

    @property
    def profile(self):
        # BUG: should be absolute path
        return '/%s' % self.nickname

    @property
    def feed(self):
        feed = {'atom': '/main/activitystreams/user_timeline/%d.atom' % self.id,
                'salmon': '/main/salmon/user/%d' % self.id,
                'hub': '/main/push/hub'}
        return feed

    def avatar(self, size=96):
        return 'http://www.gravatar.com/avatar/%s?s=%d' %\
            (md5(self.email.lower()).hexdigest(), size)
