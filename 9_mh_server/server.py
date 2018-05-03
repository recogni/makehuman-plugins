""" Socket server implementation.  Listens and reports received text.
"""
import gui3d, gui
import mh
import time
import socket

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import factory

################################################################################

MAX_BUF_SIZE = 8192

################################################################################

class ServerThread(QThread):
    """ ServerThread abstracts a threaded server using `QThread`s.
    """

    needs_exit = False  # signal server teardown
    socket     = None   # socket to listen on
    json       = None   # latest jsonCall object that needs to be processed
    conn       = None   # current connection
    port       = None


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
        self.log("Opening server socket ...")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(("127.0.0.1", self.port))
        except socket.error as e:
            self.log("Unable to bind to listen addr: " + e[1])
            return

        self.log("Server listening on port 18830")
        self.socket.listen(0)

        while not self.needs_exit:
            self.log("Waiting on new connection")
            try:
                c, a = self.socket.accept()
                if c and not self.needs_exit:
                    data = c.recv(MAX_BUF_SIZE)
                    self.log("Connected to %s:%d" % (a[0], a[1]))
                    self.log("Got data from client: %s" % (str(data)))

                    self.conn = c
                    self.emit(SIGNAL("evaluate(QString)"), data)
            except socket.error as e:
                pass


    def stop(self):
        if not self.needs_exit:
            self.log("Shutting down socket")
            self.needs_exit = True

            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error as e:
                pass
            self.socket.close()
            time.sleep(0.1)


    @factory.register(
        ["test", "debug"],
        "Test / debug command")
    def debug(self, jc):
        self.log("DEBUG COMMAND CALLED")
        jc.setData("YAY!")
        return jc
