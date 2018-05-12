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

        self.pose_lib       = app.getTask("Pose/Animate", "Pose")
        self.skel_lib       = app.getTask("Pose/Animate", "Skeleton")

        self.clothes_lib    = app.getTask("Geometries", "Clothes")
        self.eyebrows_lib   = app.getTask("Geometries", "Eyebrows")
        self.eyes_lib       = app.getTask("Geometries", "Eyes")
        self.topologies_lib = app.getTask("Geometries", "Topologies")
        self.eyelashes_lib  = app.getTask("Geometries", "Eyelashes")
        self.hair_lib       = app.getTask("Geometries", "Hair")
        self.teeth_lib      = app.getTask("Geometries", "Teeth")
        self.tongue_lib     = app.getTask("Geometries", "Tongue")


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


    """ -----------------------------------------------------------------------

        Registered makehuman commands.

    """

    """ Modeling :: Main
    """
    @factory.register(
        "set_age",
        "Set the human's age",
        ["value", float, 0, "parameter value (between 1.0 and 90.0"])
    def set_age(self, age):
        age = min(max(age, 1.0), 90.0)
        G.mhapi.modifiers.setAge(age)

    @factory.register(
        "set_weight",
        "Set the human's weight",
        ["value", float, 0, "parameter value (between 50%% and 150%%"])
    def set_weight(self, weight):
        weight = min(max(weight, 50.0), 150.0)
        G.mhapi.modifiers.setWeight(weight)

    @factory.register(
        "set_muscle",
        "Set the human's muscle",
        ["value", float, 0, "parameter value (between 0%% and 100%%"])
    def set_muscle(self, muscle):
        muscle = min(max(muscle, 0.0), 100.0)
        G.mhapi.modifiers.setMuscle(muscle)

    @factory.register(
        "set_height",
        "Set the human's height",
        ["value", float, 0, "parameter value (in cm)"])
    def set_height(self, height):
        G.mhapi.modifiers.setHeight(height)

    @factory.register(
        "set_gender",
        "Set the human's gender",
        ["value", float, 0, "parameter value (100%% is female and 0%% is male"])
    def set_gender(self, gender):
        gender = min(max(gender, 0.0), 100.0)
        G.mhapi.modifiers.setGender(gender)

    """ ------------------------------------------------------------------- """

    """ Geometries :: Clothes
    """
    @factory.register(
        "add_clothes",
        "Set the human's clothes -- these are addititve (see remove_clothes)",
        ["clothes_path", str, "data/clothes/male_casualsuit02/male_casualsuit02.mhclo", "path to clothes file"])
    def add_clothes(self, clothes_path):
        self.clothes_lib.selectProxy(clothes_path)

    @factory.register(
        "remove_clothes",
        "Remove the human's clothes -- these are addititve (see add_clothes)",
        ["clothes_path", str, "data/clothes/male_casualsuit02/male_casualsuit02.mhclo", "path to clothes file"])
    def remove_clothes(self, clothes_path):
        self.clothes_lib.deselectProxy(clothes_path)


    """ Geometries :: Eyes
    """
    @factory.register(
        "set_eyes",
        "Set the human's eyes -- should always set low-poly",
        ["eyes_path", str, "data/eyes/low-poly/low-poly.mhclo", "path to eyes file"])
    def set_eyes(self, eyes_path):
        self.eyes_lib.selectProxy(eyes_path)


    """ Geometries :: Hair
    """
    @factory.register(
        "set_hair",
        "Set the human's hair",
        ["hair_path", str, "data/hair/afro01/afro01.mhclo", "path to hair file"])
    def set_hair(self, hair_path):
        self.hair_lib.selectProxy(hair_path)


    """ Geometries :: Teeth
    """
    @factory.register(
        "set_teeth",
        "Set the human's teeth",
        ["teeth_path", str, "data/teeth/teeth_shape01/teeth_shape01.mhclo", "path to teeth file"])
    def set_teeth(self, teeth_path):
        self.teeth_lib.selectProxy(teeth_path)


    """ Geometries :: Topologies
    """
    @factory.register(
        "set_topologies",
        "Set the human's topologies",
        ["topologies_path", str, "", "path to topologies file"])
    def set_topologies(self, topologies_path):
        self.topologies_lib.selectProxy(topologies_path)


    """ Geometries :: Eyebrows
    """
    @factory.register(
        "set_eyebrows",
        "Set the human's eyebrows",
        ["eyebrows_path", str, "data/eyebrows/eyebrow001/eyebrow001.mhclo", "path to eyebrows file"])
    def set_eyebrows(self, eyebrows_path):
        self.eyebrows_lib.selectProxy(eyebrows_path)


    """ Geometries :: Eyelashes
    """
    @factory.register(
        "set_eyelashes",
        "Set the human's eyelashes",
        ["eyelashes_path", str, "data/eyelashes/eyelashes02/eyelashes02.mhclo", "path to eyelashes file"])
    def set_eyelashes(self, eyelashes_path):
        self.eyelashes_lib.selectProxy(eyelashes_path)


    """ Geometries :: Tongue
    """
    @factory.register(
        "set_tongue",
        "Set the human's tongue",
        ["tongue_path", str, None, "path to tongue file"])
    def set_tongue(self, tongue_path):
        self.tongue_lib.selectProxy(tongue_path)

    """ ------------------------------------------------------------------- """

    """ Pose/Animate :: Skeleton
    """
    @factory.register(
        "set_skeleton",
        "Set the human's skeleton from the specified .mhskel file",
        ["skel_path", str, "data/rigs/game_engine.mhskel", "path to .mhskel file"])
    def set_skeleton(self, skel_path):
        self.skel_lib.filechooser.onFileSelected(skel_path)


    """ Pose/Animate :: Pose
    """
    @factory.register(
        "set_pose",
        "Set the human's pose to the specified bvh file",
        ["pose_path", str, "data/poses/tpose.bvh", "path to pose file"])
    def set_pose(self, pose_path):
        self.pose_lib.filechooser.onFileSelected(pose_path)




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
