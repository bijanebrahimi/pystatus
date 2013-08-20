import re
import base64
import hashlib
import BeautifulSoup
import Crypto.Hash.SHA256
from Crypto.Util import number
from Crypto.PublicKey import RSA
        
from pystatus.libs.webfinger import WebfingerClient
from pystatus.libs.crypt import b64_to_num, b64_to_str, b64encode, b64decode, strip_whitespaces


class MagicSig(object):
    params = None
    @staticmethod
    def publickey(param):
        if type(param) == type(()):
            return RSA.construct((param[0], long(param[1])))
        elif type(param) == type(''):
            # import from string
            if param.startswith('RSA'):
                key_param = re.match(re.compile(r'RSA\.(.*)\.(.*)'), param).groups()
                param = (b64_to_num(key_param[0]),b64_to_num(key_param[1]))
                return MagicEnvelopeProtocol.publickey(param)
            pass
    
    def __init__(self, magic_sig, mime_type='application/magic-envelope+xml'):
        xml = BeautifulSoup.BeautifulSoup(magic_sig)
        magic_env = xml.find('me:env', {'xmlns:me': 'http://salmon-protocol.org/ns/magic-env'})

        self.data=strip_whitespaces(magic_env.find('me:data', {'type': 'application/atom+xml'}).text)
        self.data_type=xml.find('me:data').get('type').strip()
        self.data_decoded = b64_to_str(self.data).rstrip('\n')
        self.encoding=magic_env.find('me:encoding').text
        self.alg=magic_env.find('me:alg').text
        self.sig=strip_whitespaces(magic_env.find('me:sig').text)
        self.signable = '.'.join([self.data,
                                  b64encode(self.data_type),
                                  b64encode(self.encoding),
                                  b64encode(self.alg)])
