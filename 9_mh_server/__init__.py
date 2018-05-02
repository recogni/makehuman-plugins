#!/usr/bin/python

import gui3d, gui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from server import ServerThread

################################################################################

task = None

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

        box = self.addLeftWidget(gui.GroupBox("Server settings"))
        self.toggle = box.addWidget(gui.CheckBox("Server toggle"))

        @self.toggle.mhEvent
        def onClicked(e):
            if self.toggle.selected:
                self.start_server()
            else:
                self.stop_server()

        self.logbox = self.addTopWidget(gui.DocumentEdit())
        self.logbox.setText("")
        self.logbox.setLineWrapMode(gui.DocumentEdit.NoWrap)


    def log(self, msg):
        """ Logs a message to the text box `log`.
        """
        self.logbox.addText(msg + "\n")


    def evaluate(self, data, conn=None):
        self.log("Got data: %s" % (str(data)))
        jc = gui3d.app.mhapi.internals.JsonCall(str(data))
        rc = self.server.conn
        rc.send("DONE!")
        rc.close()


    def start_server(self):
        self.log("Trying to start server thread ...")
        self.server = ServerThread()
        self.logbox.connect(self.server, SIGNAL("log(QString)"), self.log)
        self.logbox.connect(self.server, SIGNAL("evaluate(QString)"), self.evaluate)
        self.server.start()


    def stop_server(self):
        self.log("Trying to close server thread ...")
        if self.server is None:
            return

        self.server.stop()
        self.server = None

################################################################################

""" Define the `load(app)` and `unload(app)` interfaces so that makehuman can
    instantiate our plugin as well.
"""

def load(app):
    global task
    category = app.getCategory("MHServer")
    task     = category.addTask(MHServerTaskView(category))


def unload(app):
    global task
    if task:
        task.stop_server()
