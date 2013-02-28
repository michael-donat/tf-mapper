__author__ = 'thornag'

import sys
from interface.main import Ui_MainWindow
from model import map, helper
from PyQt4 import QtGui, QtCore, Qt

class TFMapper(QtGui.QMainWindow):
    def __init__(self):
        super(TFMapper, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.actionHandler = helper.ActionHandler(self)
        self.registry = helper.Registry()
        self.ui.uiComponentViewingFrame.setStyleSheet('background-color: black')

        self.ui.pushButton.clicked.connect(self.debug)

        self.registry.activeWalker = walker = map.Walker(self.registry)
        walker.setDrawingMode()

        self.connectOutlets()

    def test(self, event):
        print event

    def debug(self):
        self.createNewMap()

    def validateConfig(self):
        if(helper.Config.roomSize % 6):
            raise Exception("roomSize has to be multiplication of 6")

    def connectOutlets(self):
        self.ui.menuActionNew.triggered.connect(self.actionHandler.loadNewMapAction)
        self.ui.compassN.clicked.connect(self.registry.activeWalker.goNorthFromActive)
        self.ui.compassNE.clicked.connect(self.registry.activeWalker.goNorthEastFromActive)
        self.ui.compassE.clicked.connect(self.registry.activeWalker.goEastFromActive)
        self.ui.compassSE.clicked.connect(self.registry.activeWalker.goSouthEastFromActive)
        self.ui.compassS.clicked.connect(self.registry.activeWalker.goSouthFromActive)
        self.ui.compassSW.clicked.connect(self.registry.activeWalker.goSouthWestFromActive)
        self.ui.compassW.clicked.connect(self.registry.activeWalker.goWestFromActive)
        self.ui.compassNW.clicked.connect(self.registry.activeWalker.goNorthWestFromActive)


    def createNewMap(self):
        #remove all children of uiComponentViewingFrame
        for child in self.ui.uiComponentViewingFrame.children():
            child.destroy()
        #reset Map registry
        self.Map = map.Map()
        self.Map.draw(self.ui.uiComponentViewingFrame, helper.Config.mapAreaSize)
        self.Map.updateGeometry()

        self.registry.activeMap = self.Map

        mapLevel = map.Level()
        mapLevel.draw(self.Map.widget, helper.Config.mapAreaSize)
        self.focusLevel(mapLevel)
        self.Map.addLevel(0, mapLevel)

        #create first room
        middlePoint = self.Map.getMiddlePoint(helper.Config.roomSize)

        from interface import room as iRoom

        room = iRoom.Room(mapLevel.widget, middlePoint[0], middlePoint[1], [])
        self.focusRoom(room)
        room.show()

    def focusLevel(self, mapLevel):
        self.registry.activeLevel = mapLevel
        mapLevel.widget.show()
        mapLevel.show()

    def focusRoom(self, room):
        if self.registry.activeRoom!=None:
            self.registry.activeRoom.markInActive()

        self.registry.activeRoom = room

        self.registry.activeRoom.markActive()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mapper = TFMapper()
    mapper.validateConfig()
    mapper.show()
    sys.exit(app.exec_())


