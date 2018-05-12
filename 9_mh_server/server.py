""" Socket server implementation.  Listens and reports received text.
"""
import gui3d, gui
import json
import time

import tornado
from tornado import ioloop, web, websocket, httpserver

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import factory

################################################################################

def CommandHandler(qt):
    """ `CommandHandler` wraps a HTTP POST request.

        HTTP POST /command
    """
    class _handler(web.RequestHandler):
        def get(self):
            self.write("/command only supports POST requests\r\n")
        def post(self):
            if self.request and self.request.body:
                qt.log("HTTP POST / %s" % (self.request.body))
                qt.command(self.request.body)
                self.write("OK")
    return _handler

################################################################################

def SocketHandler(qt):
    """ `SocketHandler` wraps a websocket connection.

        HTTP GET /ws
    """
    class _handler(websocket.WebSocketHandler):
        def check_origin(self, origin):
            return True
        def open(self):
            qt.log("new socket open ...")
            qt.register_socket(self)
        def on_close(self):
            qt.remove_socket(self)
        def on_message(self, msg):
            qt.log("Got socket command: %s" % (msg))
            qt.command(msg)
    return _handler

################################################################################

class ServerThread(QThread):
    """ ServerThread abstracts a threaded server using `QThread`s.
    """
    taskview = None
    port     = None
    app      = None
    server   = None
    sockets  = []

    def __init__(self, parent=None, port=18830):
        """ ServerThread constructor.
        """
        QThread.__init__(self, parent)
        self.port = port


    def run(self):
        """ `run` is invoked when the QThread is started.

            Note that this is called on a separate thread and any `mh` APIs
            that modify or query the human must be executed in the main thread.

            This is done by invoking the `command` signal to the `TaskView`.
        """
        self.sockets = []
        self.app = tornado.web.Application([
            (r"/ws",      SocketHandler(self)),
            (r"/command", CommandHandler(self)),
        ])
        self.server = httpserver.HTTPServer(self.app)

        self.log("Server listening on port :%d" % (self.port))
        self.server.listen(self.port)
        tornado.ioloop.IOLoop.current().start()


    def set_taskview(self, tv):
        """ `set_taskview` is called by the `TaskView`.  For some reason the
            `parent` property in `__init__` is None.  There must be a more
            elegant way to grab this info.
        """
        self.taskview = tv


    def add_socket(self, sock):
        """ `add_socket` allows the socket handler to register a newly connected
            socket with the server.
        """
        if sock not in self.sockets:
            self.sockets.append(sock)


    def remove_socket(self, sock):
        """ `remove_socket` removes a disconnected socket from the server's
            socket list.
        """
        if sock in self.sockets:
            self.sockets.remove(sock)


    def broadcast(self, msg):
        """ `broadcast` sends a message to all connected sockets.

            WARNING: Unless you particularly like infinite loops, do NOT call
                     ANY other class or parent class methods here.  In the
                     event that they log something, we will be :(.
        """
        for sock in self.sockets:
            try:
                sock.write_message(msg)
            except:
                pass


    def command(self, message):
        """ `command` emits the `message` as a signal to the taskview thread.
        """
        self.emit(SIGNAL("command(QString)"), QString(message))


    def log(self, message):
        """ `log` logs a message to the taskview.
        """
        self.emit(SIGNAL("log(QString)"), QString(message))
        print message


    def stop(self):
        """ `stop` stops the server socket.
        """
        if self.server:
            self.log("Server shutting down ...")
            self.server.stop()
