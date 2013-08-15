from os import path


class BaseConfiguration:
    DEBUG = True
    DEPLOYMENT = False
    CSRF_ENABLED = True

    SECRET_KEY = '\x05m\xa8\x8b\r\xd94\xc7\x81\x99\xdb\x06<-cwT\x0fk'\
        '\x88\xb9\xb6\x18\xceV\x89\xb8&*\x06\xe8\xde'

    APP_NAME = 'OstatusMini'
    BASE_DIR = path.dirname(path.abspath(__file__))
    # INSTALLED_BLUEPRINTS = ('user',)


class DevelopmentConfig(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1@localhost/ostatus_mini'
    SQLALCHEMY_ECHO = True
    DOMAIN = '127.0.0.2'
    HOST = '127.0.0.2'
    BASE_URL = 'http://%s' % DOMAIN


class DeploymentConfig(BaseConfiguration):
    DEPLOYMENT = True
    
