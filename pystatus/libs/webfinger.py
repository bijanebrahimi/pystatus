import urllib
import BeautifulSoup
from Crypto.PublicKey import RSA

from crypt import b64_to_num
# from pystatus.models import User

class WebfingerClient():
    @staticmethod
    def get_user(username):
        if username.startswith('acct:'):
            name, hostname = username.lstrip('acct:').split('@')
            user = User.query.filter(username==name).first()
            return user
        elif username.startswith('http:'):
            # TODO: is there a way get username from HTTP link?
            pass
    @staticmethod
    def normalize(username):
        if username.startswith('http'):
            # FIXME: what to do with this?
            return username
        elif username.startswith('@'):
            # FIXME: get HOSt from config
            return 'acct:%s@%s' % (username.lstrip('@'), '127.0.0.2')
        else:
            return 'acct:%s' % (username)

    @staticmethod
    def _get_lrdd(host):
        try:
            content = urllib.urlopen('http://%s/.well-known/host-meta' % host).read()
            xml = BeautifulSoup.BeautifulSoup(content)
            lrdd = xml.find('link', {'rel': 'lrdd'}).get('template')
            return lrdd
        except:
            # TODO: raise Exception
            return None
    @staticmethod
    def get_public_key(name):
        # user = WebfingerClient.get_user(username)
        # if user:
        
        username_normalized = WebfingerClient.normalize(name)
        username, host = username_normalized.lstrip('acct:').split('@')
        template = WebfingerClient._get_lrdd(host)
        try:
            content = urllib.urlopen(template.replace('{uri}', username_normalized)).read()
            xml = BeautifulSoup.BeautifulSoup(content)
            magic_publickey = xml.find('link', {'rel': 'magic-public-key'}).get('href')
            magic_publickey_mime, magic_publickey_format = magic_publickey.split(':')[1].split(',')
            publickey_type, publickey_n_string, publickey_e_string =  magic_publickey_format.split('.')
            publickey_n = b64_to_num(publickey_n_string.encode('utf-8'))
            publickey_e = b64_to_num(publickey_e_string.encode('utf-8'))
            if publickey_type == 'RSA':
                publickey = RSA.construct((long(publickey_n), long(publickey_e)))
                return publickey
        except Exception as e:
            print 'Exception: %s' % e.message
            return None
