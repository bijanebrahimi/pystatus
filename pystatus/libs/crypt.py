import re
import base64
import Crypto.Util.number
import Crypto.Random.OSRNG
import Crypto.PublicKey.RSA
        
# string
def strip_whitespaces(data):
    return re.sub(re.compile(r'[\s]+'), '', data)

# base64
def b64_to_num(data):
    data = '%s%s' % (data, '=' * (4 - len(data) % 4))
    return Crypto.Util.number.bytes_to_long(base64.urlsafe_b64decode(data))

def b64_to_str(data):
    data = '%s%s' % (data, '=' * (4 - len(data) % 4))
    return base64.urlsafe_b64decode(data.encode('utf-8'))

def b64encode(data):
    return base64.urlsafe_b64encode(data)

def b64decode(data):
    return base64.urlsafe_b64decode(data)

# cryptography
def generate_rsa_key(size=2048):
    PRNG = Crypto.Random.OSRNG.posix.new().read
    key =  Crypto.PublicKey.RSA.generate(size, PRNG)
    return key

def export_rsa_key(key):
    return key.exportKey()
