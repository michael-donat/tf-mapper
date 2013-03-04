
import di, view
import math
from PyQt4 import QtCore, QtGui

__author__ = 'thornag'

class Direction:
    N=1
    NE=2
    E=4
    SE=8
    S=16
    SW=32
    W=64
    NW=128

class Room:
    __exits=0
    __currentlyVisited=False
    __view=None
    __position=None
    __links={}
    def __init__(self, exits=0):
        self.__exits = exits

    def hasExit(self, exit_):
        return self.__exits & exit_

    def addExit(self, exit_):
        self.__exits = self.__exits | exit_

    def setCurrentlyVisited(self, bVisited):
        self.__currentlyVisited = bool(bVisited)

    def isCurrentlyVisited(self):
        return bool(self.__currentlyVisited)

    def setView(self, view):
        self.__view = view
        view.setModel(self)

    def getView(self):
        return self.__view

    def setPosition(self, QPoint):
        self.__position = QPoint
        self.__view.setPos(QtCore.QPointF(QPoint))

class CoordinatesHelper:
    __config = di.ComponentRequest('Config')

    def snapToGrid(self, QPoint):
        x = (QPoint.x() / self.__config.getSize()) * self.__config.getSize()
        y = QPoint.y() / self.__config.getSize() * self.__config.getSize()
        if QPoint.x() % self.__config.getSize() > self.__config.getMidPoint():
            x += self.__config.getSize()
        if QPoint.y() % self.__config.getSize() > self.__config.getMidPoint():
            y += self.__config.getSize()

        return QtCore.QPoint(x, y)

    def centerFrom(self, QPoint):
        return QtCore.QPoint(QPoint.x()-(self.__config.getSize()/2), QPoint.y()-(self.__config.getSize()/2))

    def movePointInDirection(self, QPoint, direction):

        moveBy = self.__config.getSize()

        if direction == Direction.N:
            newPosition = QPoint + QtCore.QPointF(0, -1 * moveBy)
        if direction == Direction.NE:
            newPosition = QPoint + QtCore.QPointF(moveBy, -1 * moveBy)
        if direction == Direction.E:
            newPosition = QPoint + QtCore.QPointF(moveBy, 0)
        if direction == Direction.SE:
            newPosition = QPoint + QtCore.QPointF(moveBy, 1 * moveBy)
        if direction == Direction.S:
            newPosition = QPoint + QtCore.QPointF(0, moveBy)
        if direction == Direction.SW:
            newPosition = QPoint + QtCore.QPointF(-1 * moveBy, moveBy)
        if direction == Direction.W:
            newPosition = QPoint + QtCore.QPointF(-1 * moveBy, 0)
        if direction == Direction.NW:
            newPosition = QPoint + QtCore.QPointF(-1 * moveBy, -1 * moveBy)

        return newPosition

class Config(object):
    __exitLength=8
    __edgeLength=21
    def getSize(self):
        return self.__edgeLength + (2 * self.__exitLength)

    def getExitLength(self):
        return self.__exitLength

    def getEdgeLength(self):
        return self.__edgeLength

    def getMidPoint(self):
        return math.ceil(self.getSize()/float(2))

class RoomFactory:
    __config = di.ComponentRequest('Config')
    __helper = di.ComponentRequest('CoordinatesHelper')

    def createInDirection(self, direction, QPoint, QGraphicsScene):
        return self.createAt(self.__helper.movePointInDirection(QPoint, direction), QGraphicsScene)

    def createAt(self, QPoint, QGraphicsScene):
        room = self.spawnRoom()
        QGraphicsScene.addItem(room.getView())
        room.setPosition(QPoint)
        boundingRect = QGraphicsScene.itemsBoundingRect()
        boundingRect.adjust(-50,-50,50,50)
        QGraphicsScene.setSceneRect(boundingRect)

        return room

    def spawnRoom(self):
        room = Room()
        viewRoom = view.Room()
        room.setView(viewRoom)
        return room

class Registry:
    currentlyVisitedRoom=None
    def __init__(self):
        pass

class Navigator:
    __config=di.ComponentRequest('Config')
    __registry=di.ComponentRequest('Registry')
    __roomFactory=di.ComponentRequest('RoomFactory')
    __coordinatesHelper=di.ComponentRequest('CoordinatesHelper')
    __enableCreation=False

    def enableCreation(self, enable):
        self.__enableCreation = bool(enable)

    def goNorth(self):
        return self.go(Direction.N, Direction.S)

    def goNorthEast(self):
        return self.go(Direction.NE, Direction.SW)

    def goEast(self):
        return self.go(Direction.E, Direction.W)

    def goSouthEast(self):
        return self.go(Direction.SE, Direction.NW)

    def goSouth(self):
        return self.go(Direction.S, Direction.N)

    def goSouthWest(self):
        return self.go(Direction.SW, Direction.NE)

    def goWest(self):
        return self.go(Direction.W, Direction.E)

    def goNorthWest(self):
        return self.go(Direction.NW, Direction.SE)

    def go(self, fromExit, toExit):

        if self.__registry.currentlyVisitedRoom is None:
            return QtGui.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtGui.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        if(self.__enableCreation):

            destinationPoint = self.__coordinatesHelper.movePointInDirection(currentRoom.getView().pos(), fromExit)
            destinationRoom = currentRoom.getView().scene().itemAt(destinationPoint)

            currentRoom.addExit(fromExit)

            if destinationRoom is not None:
                destinationRoom.getModel().addExit(toExit)
                self.markVisitedRoom(destinationRoom.getModel())
            else:
                newRoom = self.__roomFactory.createInDirection(fromExit, currentRoom.getView().pos(), currentRoom.getView().scene())
                newRoom.addExit(toExit)
                self.markVisitedRoom(newRoom)
            """
            @todo: Need to refactor this so navigator doesnt create set active
            """
        elif currentRoom.hasExit(fromExit):
            """
            @todo: This has to be changed when exit links are operational to use links rather than positions
            """
            destinationPoint = self.__coordinatesHelper.movePointInDirection(currentRoom.getView().pos(), fromExit)
            destinationRoom = currentRoom.getView().scene().itemAt(destinationPoint)
            if destinationRoom is not None:
                self.markVisitedRoom(destinationRoom.getModel())


    def markVisitedRoom(self, roomModel):
        if self.__registry.currentlyVisitedRoom is not None:
            self.__registry.currentlyVisitedRoom.setCurrentlyVisited(False)
            self.__registry.currentlyVisitedRoom.getView().update()

        self.__registry.currentlyVisitedRoom = roomModel

        roomModel.setCurrentlyVisited(True)
        roomModel.getView().clearFocus()
        roomModel.getView().scene().views()[0].centerOn(roomModel.getView())
        for item in roomModel.getView().scene().selectedItems():
            item.setSelected(False)

        roomModel.getView().update()







