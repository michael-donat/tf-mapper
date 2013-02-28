__author__ = 'thornag'

from PyQt4 import QtGui, QtCore

class RoomArea(QtGui.QWidget):
    def __init__(self):
        super(RoomArea, self).__init__()

        self.initUI()

    def initUI(self):
        pass

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawRect(10,10,11,11)
        qp.end()