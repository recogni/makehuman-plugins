""" Socket server implementation.  Listens and reports received text.
"""
import gui3d, gui
import json
import time

import tornado
from tornado import ioloop, web

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import factory

################################################################################

MAX_BUF_SIZE = 8192

################################################################################

def CommandHandler(qt):
    class _handler(tornado.web.RequestHandler):
        def get(self):
            self.write("/command only supports POST requests\r\n")
        def post(self):
            if self.request and self.request.body:
                qt.log("HTTP POST / %s" % (self.request.body))
                qt.emit(SIGNAL("evaluate(QString)"), QString(self.request.body))
                self.write("OK")
    return _handler


################################################################################

class ServerThread(QThread):
    """ ServerThread abstracts a threaded server using `QThread`s.
    """
    parent = None
    port   = None
    app    = None


    def __init__(self, parent=None, port=18830):
        QThread.__init__(self, parent)
        self.port = port


    def set_taskview(self, tv):
        self.taskview = tv


    def log(self, message):
        self.emit(SIGNAL("log(QString)"), QString(message))
        print message


    def run(self):
        """ run is invoked in a separate "QThread", this will terminate once
            the `needs_exit` boolean is setup (or if there is a failure during
            bind / startup).
        """
        self.app = tornado.web.Application([
            (r"/command", CommandHandler(self)),
        ])

        self.log("Server listening on port :%d" % (self.port))
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()


    def stop(self):
        if self.app:
            self.log("Server shutting down ...")
            self.app.stop()

