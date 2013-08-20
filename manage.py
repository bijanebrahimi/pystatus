#!/usr/bin/env python2.7

from optparse import OptionParser
from pystatus.application import create_app
from pystatus.config import DevelopmentConfig
from pystatus.scripts import create_db, user_create

parser = OptionParser()
parser.add_option("-c", "--create", dest="create",
                  help="create an object")
parser.add_option("-n", "--name", dest="name",
                  help="Objects' name")
parser.add_option("-e", "--email", dest="email",
                  help="Objects' email address")
parser.add_option("-p", "--password", dest="password",
                  help="Objects' password")

(options, args) = parser.parse_args()

print options, args
app = create_app(DevelopmentConfig)

if options.create == 'db':
    create_db()
elif options.create == 'user':
    # TODO: check for username, email and password
    user = user_create(username=options.name,
                       email=options.email,
                       password=options.password)
    print user
