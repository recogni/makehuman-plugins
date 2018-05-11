""" MH Server plugin entry-point. See the load() and unload() functions.
"""
import gui3d, gui

import mh
from core import G

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from server import ServerThread

################################################################################

class MHServerTaskView(gui3d.TaskView):

    human  = None   # Reference to the in-scene human
    toggle = None   # Toggle button for server enable / disable
    logbox = None   # Log view of any server spew


    def __init__(self, category):
        """ Constructor for the TaskView.  This accepts the category under which
            this feature is enabled.

            The category is registered with the app and passed into this
            constructor on the `load()` API below.
        """
        self.human = gui3d.app.selectedHuman
        gui3d.TaskView.__init__(self, category, "MHServer")

        fr_left = self.addLeftWidget(gui.GroupBox("Settings:"))
        self.txt_port    = fr_left.addWidget(gui.TextEdit(text="18830"))
        self.btn_restart = fr_left.addWidget(gui.Button("Restart"))
        @self.btn_restart.mhEvent
        def onClicked(e):
            self.restart_server()

        self.logbox = self.addTopWidget(gui.DocumentEdit())
        self.logbox.setText("")
        self.logbox.setLineWrapMode(gui.DocumentEdit.NoWrap)


    def log(self, msg):
        """ Logs a message to the text box `log`.
        """
        self.logbox.addText(msg + "\n")


    def evaluate(self, data, conn=None):
        self.log("Got data: %s" % (str(data)))
        print self.human.mesh


    def start_server(self):
        self.log("Trying to start server thread ...")
        self.server = ServerThread(port=int(self.txt_port.text, 10))
        self.logbox.connect(self.server, SIGNAL("log(QString)"), self.log)
        self.logbox.connect(self.server, SIGNAL("evaluate(QString)"), self.evaluate)

        self.server.set_taskview(self)
        self.server.start()


    def stop_server(self):
        self.log("Trying to close server thread ...")
        if self.server is None:
            return

        self.server.stop()
        self.server = None


    def restart_server(self):
        self.stop_server()
        self.start_server()


################################################################################

class Loader():
    task = None


    def load(self, app):
        category  = app.getCategory("MHServer")
        self.task = category.addTask(MHServerTaskView(category))
        self.task.start_server()


    def unload(self, app):
        if self.task:
            self.task.stop_server()

loader = Loader()

################################################################################

""" Interface functions required to register with makehuman's plugin system.
"""

def load(app):
    return loader.load(app)


def unload(app):
    return loader.unload(app)
