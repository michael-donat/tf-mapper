__author__ = 'thornag'

from PyQt4 import QtCore, QtGui

import di

class Level:
    __mapIndex=0
    __view=None
    __id=None
    def __init__(self, mapIndex):
        self.__mapIndex=mapIndex

    def getMapIndex(self):
        return self.__mapIndex

    def setView(self, view):
        self.__view = view
        view.setModel(self)

    def getView(self):
        return self.__view

    def setId(self, id_):
        self.__id = id_

    def getId(self):
        return self.__id

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


class Room:
    __exits=0
    __currentlyVisited=False
    __view=None
    __position=None
    __id=None
    __level=None
    __map=di.ComponentRequest('Map')
    def __init__(self, exits=0):
        self.__exits = exits
        self.__links={}

    def delete(self):
        for linkPointer in self.__links:
            link = self.__links[linkPointer]
            link.getView().scene().removeItem(link.getView())
            leftRoom = link.getLeft()
            if leftRoom[0].getId() is not self.getId(): leftRoom[0].removeExit(leftRoom[1])
            rightRoom = link.getRight()
            if rightRoom[0].getId() is not self.getId(): rightRoom[0].removeExit(rightRoom[1])
            leftRoom[0].getView().update()
            rightRoom[0].getView().update()

        del self.__links
        del self.__exits
        self.getView().scene().removeItem(self.getView())

    def exits(self):
        return self.__exits

    def setId(self, id_):
        self.__id = id_

    def getId(self):
        return self.__id

    def hasExit(self, exit_):
        return self.__exits & exit_ and exit_ in self.__links

    def addExit(self, exit_):
        self.__exits = self.__exits | exit_

    def removeExit(self, exit_):
        self.__exits = self.__exits ^ exit_
        del self.__links[exit_]

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

    def setLevel(self, level):
        self.__level = level



