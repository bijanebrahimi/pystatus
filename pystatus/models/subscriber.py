# from python
from datetime import datetime
from random import choice
from hashlib import md5

# from flask
from flask.ext.sqlalchemy import SQLAlchemy

# from friendfile
from pystatus.extensions import db


class Subscriber(db.Model):
    __tablename__ = 'subscrieber'
    id = db.Column(db.Integer, primary_key=True)
    callback = db.Column(db.String(255), nullable=False)
    secret = db.Column(db.String(255), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    verify = db.Column(db.String(255), nullable=False)
    verify_token = db.Column(db.String(255), nullable=True)
    
    created = db.Column(db.DateTime(),
                        default=datetime.now)
    modified = db.Column(db.DateTime(),
                         default=datetime.now,
                         onupdate=datetime.now)


# ('hub.verify', u'sync'), 
# ('hub.verify_token', u'25303f07d52b763a0fd05d1a2a4ed2dd'), 
# ('hub.topic', u'http://127.0.0.2/main/activitystreams/user_timeline/1.atom'), 
# ('hub.callback', u'http://sn/main/push/callback/1'), 
# ('hub.secret', u'997e9429d6f200c8b07b08f58ca4b114b3ae913838787df062d56b532ff4097c'), 
# ('hub.mode', u'subscribe')])
