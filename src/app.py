import sys
import os
import logging

from datetime import datetime
from tarfile import CONTTYPE
from flask import Flask
from argparse import ArgumentParser
from pprintpp import pformat

from appconfig import AppConfig

def parse_args(arglist):
    parser = ArgumentParser()
    parser.add_argument("-c", "--configpath", required=True, help="path to config file", type=str, default="reference.conf")
    parsedargs = parser.parse_known_args(arglist)
    return parsedargs[0]

def create_app(appconfig=None):
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return 'Hello, Mudder!'

    @app.route("/config")
    def config():
        return pformat(vars(appconfig), depth=1)

    return app

if __name__ == '__main__':
    
    print(sys.argv)

    parsedargs = parse_args(sys.argv[1:])

    appconfig = AppConfig(parsedargs.configpath)
    app = create_app(appconfig)
    
    app.run(host=appconfig.server_bind, port=appconfig.server_port)

    
    



