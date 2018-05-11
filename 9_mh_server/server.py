""" Socket server implementation.  Listens and reports received text.
"""
import gui3d, gui
import mh
import time
import socket

import tornado
from tornado import ioloop, web

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import factory

################################################################################

MAX_BUF_SIZE = 8192

################################################################################

class PingHandler(tornado.web.RequestHandler):
    def get(self):
        print "HTTP GET /"
        self.write("GET /")


class AgeHandler(tornado.web.RequestHandler):
    def get(self):
        print "HTTP GET /age"
        self.write("GET /age")

################################################################################

class ServerThread(QThread):
    """ ServerThread abstracts a threaded server using `QThread`s.
    """
    port = None
    app  = None


    def __init__(self, parent=None, port=18830):
        QThread.__init__(self, parent)
        self.port = port


    def log(self, message):
        self.emit(SIGNAL("log(QString)"), QString(message))
        print message


    def run(self):
        """ run is invoked in a separate "QThread", this will terminate once
            the `needs_exit` boolean is setup (or if there is a failure during
            bind / startup).
        """
        routes = [
            (r"/",     PingHandler),
            (r"/ping", PingHandler),
        ]
        routes.extend(factory.get_routes())
        self.app = tornado.web.Application(routes)

        print "Server listening on port :%d" % (self.port)
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()


    def stop(self):
        if self.app:
            print "Server shutting down ..."
            self.app.stop()

