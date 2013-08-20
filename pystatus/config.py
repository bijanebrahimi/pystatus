from os import path


class BaseConfiguration:
    DEBUG = True
    DEPLOYMENT = False
    CSRF_ENABLED = True

    SECRET_KEY = '#\x80\x9e\x16\xb0PH\x0c\xd1\xe8\xcfy\x1e\xaa\xc9\xed\x0f\xac\x90\xba,\xa9:\xe4B\x17\xf5\xff\xe4C\xf0\xf4'

    # Crypto.Random.OSRNG.posix.new().read(32)
    CRYPTO_AES_KEY = '#\x80\x9e\x16\xb0PH\x0c\xd1\xe8\xcfy\x1e\xaa\xc9\xed\x0f\xac\x90\xba,\xa9:\xe4B\x17\xf5\xff\xe4C\xf0\xf4'
    CRYPTO_AES_IV = '\xfc\x999\xaa\xad\xea\r\x00E?8\x10\xf3\xb2\xb2\x9c'

    APP_NAME = 'OstatusMini'
    BASE_DIR = path.dirname(path.abspath(__file__))
    # INSTALLED_BLUEPRINTS = ('user',)


class DevelopmentConfig(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1@localhost/pystatus'
    SQLALCHEMY_ECHO = True
    DOMAIN = '127.0.0.2'
    HOST = '127.0.0.2'
    BASE_URL = 'http://%s' % DOMAIN


class DeploymentConfig(BaseConfiguration):
    DEPLOYMENT = True
    
