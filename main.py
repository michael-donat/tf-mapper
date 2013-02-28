#!/usr/bin/python

# tetris.py

__author__ = 'thornag'

import sys
import random
from app_ui import Ui_MainWindow

from PyQt4 import QtCore, QtGui, Qt

class Drawer:
    frame = None
    @staticmethod
    def drawRoom(x, y, exits):

        #before we draw lets check if there is already a room at given coordinates
        possibleRoom = Drawer.frame.childAt(x, y)

        print possibleRoom if possibleRoom else 'NO ROOM'

        if possibleRoom:
            #no need to draw again, just link rooms again if needed
            return

        return Room(Drawer.frame, x, y, exits)

    @staticmethod
    def drawSEFrom(room, exits):
        return Drawer.drawRoom(room.x+Room.edgeSize, room.y+Room.edgeSize, exits)

    @staticmethod
    def drawEFrom(room, exits):
        return Drawer.drawRoom(room.x+Room.edgeSize, room.y, exits)

    @staticmethod
    def drawNFrom(room, exits):
        return Drawer.drawRoom(room.x, room.y-Room.edgeSize, exits)

    @staticmethod
    def drawSWFrom(room, exits):
        return Drawer.drawRoom(room.x-Room.edgeSize, room.y+Room.edgeSize, exits)

class TFMapperRegistry:
    activeRoom=None

class TFMapper(QtGui.QMainWindow):

    def __init__(self):
        super(TFMapper, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        Drawer.frame = self.ui.frame

        room = Drawer.drawRoom(150, 150, ['ne', 'e'])
        room = Drawer.drawEFrom(room, ['w', 'n'])
        room = Drawer.drawNFrom(room, ['sw', 's'])
        room = Drawer.drawSWFrom(room, ['ne'])

class Map:
    """
    Class to hold map data (rooms, links, etc)
    """
    def __init__(self):
        pass

class Link:
    """
    Represents links between rooms, each room should have a link from one exit to another
    """
    def __init__(self):
        pass

class Room(QtGui.QWidget):
    edgeSize=90
    def __init__(self, parent, x, y, exits):
        super(Room, self).__init__(parent)
        self.exits = exits
        self.x = x
        self.y = y
        self.initUI()
        print str.format("Creating room at x:{0}, y:{1}", x, y)
        self.activecolor = '#FF0000'
        self.idlecolor = '#000000'

        self.bordercolor = self.idlecolor

    def markActive(self):
        self.bordercolor = self.activecolor
        self.repaint()
        if hasattr(TFMapperRegistry.activeRoom, 'markInActive'):
            TFMapperRegistry.activeRoom.markInActive()
        TFMapperRegistry.activeRoom = self

    def markInActive(self):
        self.repaint()

    def mousePressEvent(self, QMouseEvent):
        self.markActive()

    def initUI(self):

        self.setGeometry(self.x, self.y, self.edgeSize, self.edgeSize)

    def paintEvent(self, e):
        print 'PAINTING with'+self.bordercolor
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor(self.bordercolor)

        pen = QtGui.QPen(color)
        pen.setWidth(1)

        qp = QtGui.QPainter()

        sizeChunk = self.edgeSize / 6

        qp.begin(self)
        qp.setPen(pen)

        qp.drawRect(sizeChunk, sizeChunk, sizeChunk*4, sizeChunk*4)
        qp.drawText(sizeChunk+10, sizeChunk+10, str.format("{0}x{1}", self.x, self.y))
        qp.end()

        qp.begin(self)
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor(self.idlecolor)
        pen.setColor(color)
        qp.setPen(pen)


        if 'n' in self.exits:
            qp.drawLine(sizeChunk*3, 0, sizeChunk*3, sizeChunk)
        if 'ne' in self.exits:
            qp.drawLine(sizeChunk*5, sizeChunk, sizeChunk*6, 0)
        if 'e' in self.exits:
            qp.drawLine(sizeChunk*5, sizeChunk*3, sizeChunk*6, sizeChunk*3)
        if 'se' in self.exits:
            qp.drawLine(sizeChunk*3, sizeChunk*3, sizeChunk*4, sizeChunk*4)
        if 's' in self.exits:
            qp.drawLine(sizeChunk*3, sizeChunk*5, sizeChunk*3, sizeChunk*6)
        if 'sw' in self.exits:
            qp.drawLine(0, sizeChunk*6, sizeChunk, sizeChunk*5)
        if 'w' in self.exits:
            qp.drawLine(0, sizeChunk*3, sizeChunk*1, sizeChunk*3)
        if 'nw' in self.exits:
            qp.drawLine(0, 0, sizeChunk, sizeChunk)
        qp.end()

        self.bordercolor = self.idlecolor


app = QtGui.QApplication(sys.argv)
mapper = TFMapper()
mapper.show()
sys.exit(app.exec_())