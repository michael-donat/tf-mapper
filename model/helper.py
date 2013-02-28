
from PyQt4 import QtGui

class ActionHandler:
    mainWindow=None
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

    def loadNewMapAction(self):
        if QtGui.QMessageBox.No == QtGui.QMessageBox.question(self.mainWindow, "Are you sure?", "Do you want to start a new map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No):
            return

        self.mainWindow.createNewMap()


class Config:
    roomSize = 12
    mapAreaSize = 10000

class Registry:
    activeMap=None
    activeLevel=None
    activeRoom=None
    activeWalker=None
