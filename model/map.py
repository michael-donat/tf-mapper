__author__ = 'thornag'

from PyQt4 import QtGui, QtCore

from interface.room import Room
from model import helper

class Direction:
    N   =   1
    NW  =   2
    E   =   4
    SE  =   8
    S   =   16
    SW  =   32
    W   =   64
    NE  =   128
    U   =   256
    D   =   512



class Map(QtCore.QObject):
    mapLevels = {}
    def __init__(self):
        super(Map, self).__init__()

    def getMiddlePoint(self, gridSpacing):
        middlePoint = self.widget.width()/2
        modMiddlePoint = middlePoint % gridSpacing
        middlePointOnGrid = middlePoint - modMiddlePoint
        return (middlePointOnGrid, middlePointOnGrid)


    def draw(self, parent, size):
        self.widget= QtGui.QWidget(parent)
        self.widget.setStyleSheet("background-color: #E8E8E8")
        self.widget.setGeometry(0, 0, size, size)
        self.widget.installEventFilter(self)
        self.widget.show()

    def updateGeometry(self, x=None, y=None):

        print 'updateGeometry called with x:'+str(x)+' y:'+str(y)

        x = self.widget.width() / 2 if x is None else x
        y = self.widget.height() / 2 if y is None else y

        self.lastRequestedGeometry = (x, y)

        parent = self.widget.parentWidget()

        hookPointX = x - (parent.width()/2)
        hookPointY = y - (parent.height()/2)

        print 'updateGeometry has parent size of x:'+str(parent.width())+' y:'+str(parent.height())
        print 'updateGeometry is setting hook points x:'+str(hookPointX)+' y:'+str(hookPointY)

        self.widget.move(-1 * hookPointX, -1 * hookPointY)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.updateGeometry(event.x(), event.y())

        if event.type() == QtCore.QEvent.Paint:
            self.updateGeometry(self.lastRequestedGeometry[0], self.lastRequestedGeometry[1])

        return False

    def addLevel(self, index, mapLevel):
        mapLevel.setIndex(index)
        self.mapLevels[index] = mapLevel



class Level:
    index=None
    """
    Represents a widget within the display frame that acts as a
    map level, every map room should belong to a map level
    """

    def draw(self, parent, size):
        self.widget= QtGui.QWidget(parent)
        self.widget.setGeometry(0, 0, size, size)
        self.widget.show()

    def show(self):
        self.widget.raise_()

    def setIndex(self, index):
        self.index = index


class Room:
    exits={}
    """
    Represents a room on a map, has it's own coordinates relative to
    area level (canvas/widget at which map is drawn)
    """
    def hasExit(self, exit):
        return exit in self.exits


class Exit:
    """
    Represents a room on a map, has it's own coordinates relative to
    area level (canvas/widget at which map is drawn)
    """
    def __init__(self):
        pass

class Link:
    """
    Represents a link betwee two exists, every exit should have a link if it(exit) is connected
     to another room's exit
    """
    def __init__(self):
        pass

class Walker(QtCore.QObject):
    currentWalker=None
    drawingWalker=None
    movingWalker=None
    registry=None
    def __init__(self, registry):
        super(Walker, self).__init__()
        self.drawingWalker=DrawingWalker()
        self.registry = registry

    def setDrawingMode(self):
        self.currentWalker=self.drawingWalker

    def setMovingMode(self):
        self.currentWalker=self.movingWalker

    def goFromActive(self, toDirection, fromDirection):
        currentRoom = self.registry.activeRoom
        if(not currentRoom):
            return
        self.currentWalker.goFrom(currentRoom, toDirection, fromDirection)

    def goNorthFromActive(self):
        self.goFromActive(Direction.N, Direction.S)

    def goNorthEastFromActive(self):
        self.goFromActive(Direction.NE, Direction.SW)

    def goEastFromActive(self):
        self.goFromActive(Direction.W, Direction.E)

    def goSouthEastFromActive(self):
        self.goFromActive(Direction.SE, Direction.NW)

    def goSouthFromActive(self):
        self.goFromActive(Direction.S, Direction.N)

    def goSouthWestFromActive(self):
        self.goFromActive(Direction.SW, Direction.NE)

    def goWestFromActive(self):
        self.goFromActive(Direction.W, Direction.E)

    def goNorthWestFromActive(self):
        self.goFromActive(Direction.NW, Direction.SE)

class DrawingWalker:
    def goFrom(self, fromRoom, toDirection, fromDirection):
        if(not fromRoom.hasExit(fromDirection)):
            fromRoom.addExit(fromDirection)

        outExit = fromRoom.getExit(fromDirection)

        x = fromRoom.x()
        y = fromRoom.y()

        if toDirection==Direction.N:
            y -= helper.Config.roomSize

        toRoom = Room(self.registry.mapLevel, x, y, toDirection)

        inExit = toRoom.getExit(toDirection)

