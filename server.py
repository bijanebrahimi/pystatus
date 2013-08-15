#!/usr/bin/env python2.7

from pystatus.config import DevelopmentConfig as config
from pystatus.application import create_app

if __name__ == "__main__":
    app = create_app(config)
    app.run(host='127.0.0.2', port=80)
