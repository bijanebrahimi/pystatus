# from python
from datetime import datetime
from random import choice
from hashlib import md5
import Crypto
from base64 import urlsafe_b64encode, urlsafe_b64decode

# from flask
from flask.ext.sqlalchemy import SQLAlchemy

# from friendfile
from pystatus.extensions import db
from pystatus.libs.crypt import generate_rsa_key, export_rsa_key
from pystatus.config import BaseConfiguration


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    nickname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(200), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=True)
    
    remote = db.Column(db.Boolean, default=False, nullable=False)
    uri_profile = db.Column(db.String(255), nullable=True)
    uri_feed = db.Column(db.String(255), nullable=True)
    uri_salmon = db.Column(db.String(255), nullable=True)
    
    created = db.Column(db.DateTime(),
                        default=datetime.now)
    modified = db.Column(db.DateTime(),
                         default=datetime.now,
                         onupdate=datetime.now)

    def __init__(self, username, email, password, nickname=None, remote=False, profile_uri=None, feed_uri=None, salmon_uri=None, publickey=None):
        self.username = username
        self.email = email
        self.password = password
        if nickname is None:
            self.nickname = username
        if remote == True:
            self.uri_profile = profile_uri
            self.uri_feed = feed_uri
            self.uri_salmon = salmon_uri
            # TODO: check if it's None
            self.key = publickey

    @property
    def profile_uri(self):
        if self.remote:
            return self.uri_profile
        else:
            # FIXME: get HOST from config
            return 'http://127.0.0.2/%s' % self.nickname

    @property
    def salmon_uri(self):
        if self.remote:
            return self.uri_salmon
        else:
            # FIXME: get HOST from config
            return 'http://127.0.0.2/main/salmon/user/%d' % self.id

    @property
    def feed_uri(self):
        if self.remote:
            return self.uri_feed
        else:
            # FIXME: get HOST from config
            return 'http://127.0.0.2/main/activitystreams/user_timeline/%d.atom' % self.id
        return feed

    @property
    def public_key(self):
        key = Crypto.PublicKey.RSA.importKey(str(self.key))
        return key.publickey().exportKey()

    @property
    def magic_public_key(self):
        key = Crypto.PublicKey.RSA.importKey(str(self.key))
        return 'RSA' + '.' + urlsafe_b64encode(str(key.n)) + '.' + urlsafe_b64encode(str(key.e))

    def avatar(self, size=96):
        return 'http://www.gravatar.com/avatar/%s?s=%d' %\
            (md5(self.email.lower()).hexdigest(), size)

    @staticmethod
    def generate_key(size=1024):
        pv_key = generate_rsa_key(size)
        generate_key = export_rsa_key(pv_key)
        # TODO: should be encrypted first
        return generate_key

    @staticmethod
    def find(username):
        if username:
            try:
                return User.query.filter(User.username==username).one()
            except:
                pass

User.key = db.Column(db.Binary,
                     nullable=False,
                     default=User.generate_key())
