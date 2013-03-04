
import di, view
import math, uuid
from PyQt4 import QtCore, QtGui


__author__ = 'thornag'

class Map:
    __rooms={}
    def registerRoom(self, room):
        self.__rooms[room.getId()] = room

class Link:
    __view=None
    __left=None
    __right=None
    def setView(self, view):
        self.__view = view
        view.setModel(self)

    def getView(self):
        return self.__view

    def setLeft(self, room, exit_):
        self.__left = (room, exit_)

    def setRight(self, room, exit_):
        self.__right = (room, exit_)

    def getLeft(self):
        return self.__left

    def getRight(self):
        return self.__right

    def pointsAt(self, room):
        return self.__left[0].getId() == room.getId() or self.__right[0].getId() == room.getId()

    def getDestinationFor(self, room):
        if room.getId() == self.__left[0].getId():
            return self.__right[0]
        if room.getId() == self.__right[0].getId():
            return self.__left[0]

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
    __id=None
    def __init__(self, exits=0):
        self.__exits = exits
        self.__links={}

    def setId(self, id_):
        self.__id = id_

    def getId(self):
        return self.__id

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

    def hasLinkAt(self, direction):
        return direction in self.__links

    def linkAt(self, direction):
        return self.__links[direction]

    def addLink(self, exit_, link):
        self.__links[exit_] = link

    def getLinks(self):
        return self.__links

class CoordinatesHelper:
    __config = di.ComponentRequest('Config')

    def getExitPoint(self, exitDescription):
        room, direction = exitDescription

        QPoint = QtCore.QPointF(room.getView().x(), room.getView().y())

        objectSize = self.__config.getSize()
        midPoint = self.__config.getMidPoint()

        if direction == Direction.N:
            newPosition = QPoint + QtCore.QPointF(midPoint, 0)
        if direction == Direction.NE:
            newPosition = QPoint + QtCore.QPointF(objectSize, 0)
        if direction == Direction.E:
            newPosition = QPoint + QtCore.QPointF(objectSize, midPoint)
        if direction == Direction.SE:
            newPosition = QPoint + QtCore.QPointF(objectSize, objectSize)
        if direction == Direction.S:
            newPosition = QPoint + QtCore.QPointF(midPoint, objectSize)
        if direction == Direction.SW:
            newPosition = QPoint + QtCore.QPointF(0, objectSize)
        if direction == Direction.W:
            newPosition = QPoint + QtCore.QPointF(0, midPoint)
        if direction == Direction.NW:
            newPosition = QPoint + QtCore.QPointF(0, 0)

        return newPosition

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

    def getSelectionAreaFromPoint(self, QPointF):
        return QtCore.QRectF(QPointF.x()+self.__config.getExitLength(), QPointF.y()+self.__config.getExitLength(), self.__config.getEdgeLength(), self.__config.getEdgeLength())

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
    __map = di.ComponentRequest('Map')

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
        room.setId(uuid.uuid1())
        viewRoom = view.Room()
        room.setView(viewRoom)
        self.__map.registerRoom(room)
        return room

    def spawnLink(self):
        link = Link()
        viewLink = view.Link()
        link.setView(viewLink)
        return link

    def linkRooms(self, leftRoom, leftExit, rightRoom, rightExit, QGraphicsScene):
        #need to validate first
        if(leftRoom.hasLinkAt(leftExit) and not leftRoom.linkAt(leftExit).pointsAt(rightRoom)):
            raise Exception('Left room already links somewhere through given exit')

        if(rightRoom.hasLinkAt(rightExit) and not rightRoom.linkAt(rightExit).pointsAt(leftRoom)):
            raise Exception('Left room already links somewhere through given exit')

        #good to link
        link = self.spawnLink()
        link.setLeft(leftRoom, leftExit)
        link.setRight(rightRoom, rightExit)
        leftRoom.addLink(leftExit, link)
        rightRoom.addLink(rightExit, link)

        link.getView().redraw()
        QGraphicsScene.addItem(link.getView())


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
        return self.goFromActive(Direction.N, Direction.S)

    def goNorthEast(self):
        return self.goFromActive(Direction.NE, Direction.SW)

    def goEast(self):
        return self.goFromActive(Direction.E, Direction.W)

    def goSouthEast(self):
        return self.goFromActive(Direction.SE, Direction.NW)

    def goSouth(self):
        return self.goFromActive(Direction.S, Direction.N)

    def goSouthWest(self):
        return self.goFromActive(Direction.SW, Direction.NE)

    def goWest(self):
        return self.goFromActive(Direction.W, Direction.E)

    def goNorthWest(self):
        return self.goFromActive(Direction.NW, Direction.SE)

    def goFromActive(self, fromExit, toExit):
        if self.__registry.currentlyVisitedRoom is None:
            return QtGui.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtGui.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        return self.go(currentRoom, fromExit, toExit)

    def go(self, currentRoom, fromExit, toExit):

        if currentRoom.hasExit(fromExit):
            """
            @todo: This has to be changed when exit links are operational to use links rather than positions
            """

            exitLink = currentRoom.linkAt(fromExit)
            destinationRoom = exitLink.getDestinationFor(currentRoom)
            self.markVisitedRoom(destinationRoom)

        elif (self.__enableCreation):

            destinationRoom=None
            destinationPoint = self.__coordinatesHelper.movePointInDirection(currentRoom.getView().pos(), fromExit)
            for item in currentRoom.getView().scene().items(self.__coordinatesHelper.getSelectionAreaFromPoint(destinationPoint)):
                if isinstance(item, view.Room):
                    destinationRoom = item
                    break

            currentRoom.addExit(fromExit)

            if destinationRoom is not None:
                destinationRoom.getModel().addExit(toExit)
                self.markVisitedRoom(destinationRoom.getModel())
                newRoom = destinationRoom.getModel()
            else:
                newRoom = self.__roomFactory.createInDirection(fromExit, currentRoom.getView().pos(), currentRoom.getView().scene())
                newRoom.addExit(toExit)
                self.markVisitedRoom(newRoom)

            self.__roomFactory.linkRooms(currentRoom, fromExit, newRoom, toExit, currentRoom.getView().scene())
            """
            @todo: Need to refactor this so navigator doesnt create set active
            """





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







