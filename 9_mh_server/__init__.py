""" MH Server plugin entry-point. See the load() and unload() functions.
"""
import gui3d, gui

import mh
from core import G

from PyQt4.QtCore import *
from PyQt4.QtGui  import *

from server import ServerThread

################################################################################

class MHServerTaskView(gui3d.TaskView):

    human  = None   # Reference to the in-scene human
    toggle = None   # Toggle button for server enable / disable
    logbox = None   # Log view of any server spew
    server = None   # ServerThread instance


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


    def bootstrap(self, app):
        """ `bootstrap` allows this TaskView to figure out dependent task views
            to trigger downstream functions.
        """
        self.pose_lib = app.getTask("Pose/Animate", "Pose")
        self.skel_lib = app.getTask("Pose/Animate", "Skeleton")


    def log(self, msg):
        """ Logs a message to the text box `log`.
        """
        self.logbox.addText(msg + "\n")
        if self.server:
            self.server.broadcast(str(msg))


    def command(self, msg, conn=None):
        words     = str(msg).rstrip().split(" ")
        cmd, args = words[0], words[1:]
        factory.run(self, cmd, args)


    def start_server(self):
        self.log("Trying to start server thread ...")
        self.server = ServerThread(port=int(self.txt_port.text, 10))
        self.logbox.connect(self.server, SIGNAL("log(QString)"), self.log)
        self.logbox.connect(self.server, SIGNAL("command(QString)"), self.command)

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


    @factory.register(
        ["test", "debug"],
        "Test / debug command",
        ["x", int, 1, "x value"],
        ["y", int, 2, "y value"],
        ["z", int, 3, "z value"])
    def debug(self, x, y, z):
        self.log("Got debug(%d, %d, %d)" % (x, y, z))


    @factory.register(
        "set_pose",
        "Set the humans pose to the specified bvh file",
        ["pose_path", str, "data/poses/tpose.bvh", "path to pose file"])
    def set_human_pose(self, pose_path):
        # Trigger the QT file chooser action with our pose_path to trick the
        # 3_libraries_pose.py module to load the correct pose.
        self.pose_lib.filechooser.onFileSelected(pose_path)


    @factory.register(
        "set_skeleton",
        "Set the humans skeleton from the specified .mhskel file",
        ["skel_path", str, "data/rigs/game_engine.mhskel", "path to .mhskel file"])
    def set_human_skeleton(self, skel_path):
        self.skel_lib.filechooser.onFileSelected(skel_path)



################################################################################

class Loader():
    task = None

    def load(self, app):
        category = app.getCategory("MHServer")

        self.task = category.addTask(MHServerTaskView(category))
        self.task.bootstrap(app)
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
