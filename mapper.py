__author__ = 'thornag'

import sys
from interface.main import Ui_MainWindow
from model import map
from PyQt4 import QtGui, QtCore

class TFMapperActionHandler:
    mainWindow=None
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

    def loadNewMapAction(self):
        if QtGui.QMessageBox.No == QtGui.QMessageBox.question(self.mainWindow, "Are you sure?", "Do you want to start a new map?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No):
            return

        self.mainWindow.createNewMap()



class TFMapper(QtGui.QMainWindow):
    def __init__(self):
        super(TFMapper, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.actionHandler = TFMapperActionHandler(self)
        self.ui.uiComponentViewingFrame.setStyleSheet('background-color: black')

        self.ui.pushButton.clicked.connect(self.debug)

        self.connectOutlets()

    def debug(self):
        self.createNewMap()

    def connectOutlets(self):
        self.ui.menuActionNew.triggered.connect(self.actionHandler.loadNewMapAction)

    def createNewMap(self):
        #remove all children of uiComponentViewingFrame
        for child in self.ui.uiComponentViewingFrame.children():
            child.destroy()
        #reset Map registry
        self.Map = map.Map()
        self.Map.draw(self.ui.uiComponentViewingFrame, 10000)
        self.Map.updateGeometry()

        from interface.room import Room

        room = Room(self.Map.widget, self.Map.getMiddlePoint(), self.Map.getMiddlePoint(), ['e'])
        room.show()
        room = Room(self.Map.widget, self.Map.getMiddlePoint()+Room.edgeSize, self.Map.getMiddlePoint(), ['e', 'w'])
        room.show()
        room = Room(self.Map.widget, self.Map.getMiddlePoint()+(2*Room.edgeSize), self.Map.getMiddlePoint(), ['w'])
        room.show()

        self.Map.updateGeometry(self.Map.getMiddlePoint()+(2*Room.edgeSize), self.Map.getMiddlePoint())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mapper = TFMapper()
    mapper.show()
    sys.exit(app.exec_())


