import atexit
from concurrent.futures import thread
import logging
import os
import signal
import sys
import threading

from argparse import ArgumentParser
from datetime import datetime
from flask import Flask
from mudclient import MudClient
from pprintpp import pformat
from tarfile import CONTTYPE
from traceback import print_tb
from appconfig import AppConfig
from mudclient import MudClient

def parse_args(arglist):
    parser = ArgumentParser()
    parser.add_argument("-c", "--configpath", required=True, help="path to config file", type=str, default="reference.conf")
    parsedargs = parser.parse_known_args(arglist)
    return parsedargs[0]

def excepthook(self, type_, value, traceback):
    print(type_)
    print(value)    
    print_tb(traceback)
    sys.exit(1)

def on_exit(mudclient):
    print("Application closed")
    mudclient.stop()
    sys.exit(0)

def create_app(appconfig=None,mudclient=None):
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return 'Hello, Mudder!'

    @app.route("/config")
    def config():
        return pformat(vars(appconfig), depth=1)

    @app.route("/client")
    def client():
        return pformat(mudclient, depth=1)

    return app

if __name__ == '__main__':
    
    print(sys.argv)

    parsedargs = parse_args(sys.argv[1:])

    appconfig = AppConfig(parsedargs.configpath)

    app = create_app(appconfig)
    
    mudclient = MudClient(appconfig)

   # atexit.register(on_exit(mudclient))
    
    # threading.excepthook = excepthook(mudclient)

    mudclient.start()

    app.run(host=appconfig.server_bind, port=appconfig.server_port)

    
    



