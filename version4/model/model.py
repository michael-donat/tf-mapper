
import di, view
import math, uuid
from entity import *
from PyQt4 import QtCore, QtGui
import json, base64

__author__ = 'thornag'

class Map:
    __rooms={}
    __levels={}
    __links={}
    def levels(self):
        return self.__levels

    def rooms(self):
        return self.__rooms

    def links(self):
        return self.__links

    def registerRoom(self, room):
        self.__rooms[room.getId()] = room

    def registerLevel(self, level):
        self.__levels[level.getMapIndex()] = level

    def removeRoom(self, room):
        del self.__rooms[room.getId()]

    def registerLink(self, link):
        self.__links[link.getId()] = link

    def removeLink(self, link):
        del self.__links[link.getId()]


class Direction:
    N=1
    NE=2
    E=4
    SE=8
    S=16
    SW=32
    W=64
    NW=128
    U=256
    D=512
    OTHER=1024

    @staticmethod
    def mapFromLabel(label):
        if str.upper(str(label)) == 'CUSTOM': label='OTHER'
        return getattr(Direction, str.upper(str(label)))

    @staticmethod
    def mapToLabel(exit):
        if exit == Direction.N: return 'N'
        if exit == Direction.NE: return 'NE'
        if exit == Direction.E: return 'E'
        if exit == Direction.SE: return 'SE'
        if exit == Direction.S: return 'S'
        if exit == Direction.SW: return 'SW'
        if exit == Direction.W: return 'W'
        if exit == Direction.NW: return 'NW'
        if exit == Direction.U: return 'Up'
        if exit == Direction.D: return 'Down'
        if exit == Direction.OTHER: return 'Other/Custom'


class CoordinatesHelper:
    __config = di.ComponentRequest('Config')

    def getExitPointFromPoint(self, QPointF, direction):
        QPoint = QtCore.QPointF(QPointF.x(), QPointF.y())

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
        if direction == Direction.OTHER:
            newPosition = QPoint + QtCore.QPointF(midPoint, midPoint)

        return newPosition

    def getExitPoint(self, exitDescription):
        room, direction, label = exitDescription

        return self.getExitPointFromPoint(room.getView().pos(), direction)



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
    __exitLength=10
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
    __registry = di.ComponentRequest('Registry')
    def createInDirection(self, direction, QPoint, QGraphicsScene):
        return self.createAt(self.__helper.movePointInDirection(QPoint, direction), QGraphicsScene)

    def pasteAt(self, QPoint, QGraphicsScene, data):
        for room in data['rooms']:
            self.createAt(QtCore.QPointF(QPoint.x()+room[0],QPoint.y()+room[1]), QGraphicsScene, room[2])
        rooms = self.__map.rooms()
        for link in data['links']:
            leftRoom, leftExit = link[:2]
            rightRoom, rightExit = link[2:]
            if leftRoom not in rooms or rightRoom not in rooms: continue
            leftRoom = rooms[str(leftRoom)]
            rightRoom = rooms[str(rightRoom)]

            leftRoom.addExit(leftExit)
            rightRoom.addExit(rightExit)

            self.linkRooms(leftRoom, leftExit, rightRoom, rightExit, QGraphicsScene)

    def createLabelAt(self, QPoint, QGraphicsScene, labeltext='LABEL'):
        text = view.Label(labeltext)
        QGraphicsScene.addItem(text)
        text.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsFocusable | QtGui.QGraphicsItem.ItemIsMovable);
        text.setPos(QtCore.QPointF(QPoint))

    def createAt(self, QPoint, QGraphicsScene, Id=None, properties=None):
        if properties is None:
            properties={}
            properties[Room.PROP_COLOR] = str(self.__registry.defColor)
        room = self.spawnRoom(Id, properties)
        QGraphicsScene.addItem(room.getView())
        room.setPosition(QPoint)
        boundingRect = QGraphicsScene.itemsBoundingRect()
        boundingRect.adjust(-50,-50,50,50)
        QGraphicsScene.setSceneRect(boundingRect)
        room.setLevel(QGraphicsScene.getModel())
        return room

    def spawnRoom(self, id=None, properties=None):
        room = Room(0, properties)
        id_ = uuid.uuid1() if id==None else id
        room.setId(id_)
        viewRoom = view.Room()
        room.setView(viewRoom)
        self.__map.registerRoom(room)
        return room

    def spawnLink(self, linkLess=False, id=None, isCustomLink=False):
        #print isCustomLink
        link = Link() if not isCustomLink else CustomLink()
        id_ = uuid.uuid1() if id==None else id
        link.setId(id_)
        self.__map.registerLink(link)
        if(linkLess): return link
        viewLink = view.Link()
        link.setView(viewLink)
        return link

    def linkRoomsBetweenLevels(self, leftRoom, leftExit, rightRoom, rightExit):
        return self.linkRooms(leftRoom, leftExit, rightRoom, rightExit)


    def linkRooms(self, leftRoom, leftExit, rightRoom, rightExit, QGraphicsScene=None, leftLinkCustomLabel=None, rightLinkCustomLabel=None):
        #need to validate first
        if(Direction.OTHER != leftExit and leftRoom.hasLinkAt(leftExit) and not leftRoom.linkAt(leftExit).pointsAt(rightRoom)):
            raise Exception('Left room already links somewhere through given exit')

        if(Direction.OTHER != rightExit and rightRoom.hasLinkAt(rightExit) and not rightRoom.linkAt(rightExit).pointsAt(leftRoom)):
            raise Exception('Right room already links somewhere through given exit')

        #good to link
        link = self.spawnLink(QGraphicsScene is None, None, Direction.OTHER in [leftExit, rightExit])
        link.setLeft(leftRoom, leftExit, leftLinkCustomLabel)
        link.setRight(rightRoom, rightExit, rightLinkCustomLabel)
        leftRoom.addLink(leftExit, link)
        rightRoom.addLink(rightExit, link)

        if QGraphicsScene is None: return

        link.getView().redraw()
        QGraphicsScene.addItem(link.getView())

    def spawnLevel(self, mapIndex, id=None):
        level = Level(mapIndex)
        id_ = uuid.uuid1() if id==None else id
        level.setId(id_)
        viewLevel = view.uiMapLevel()
        viewLevel.setBackgroundBrush(QtGui.QColor(217, 217, 217))
        level.setView(viewLevel)
        self.__map.registerLevel(level)
        return level


class Registry:
    currentlyVisitedRoom=None
    roomShadow=None
    defColor=None
    def __init__(self):
        self.__rooms=[]

    def setDefaultColor(self, color):
        if isinstance(color, QtGui.QColor):
            color = color.name()
        if not len(color): self.defColor=None
        else: self.defColor=str(color)


class Navigator(QtCore.QObject):
    roomSelectedSignal=QtCore.pyqtSignal(object)
    __map=di.ComponentRequest('Map')
    __config=di.ComponentRequest('Config')
    __registry=di.ComponentRequest('Registry')
    __roomFactory=di.ComponentRequest('RoomFactory')
    __coordinatesHelper=di.ComponentRequest('CoordinatesHelper')
    __enableCreation=False
    __enableAutoPlacement=True
    __properties=di.ComponentRequest('Properties')
    def __init__(self):
        super(Navigator, self).__init__()

    def switchLevel(self, newLevel):
        levels = self.__map.levels()
        if newLevel in levels:
            view = self.__registry.currentLevel.getView().views()[0]
            self.__registry.mainWindow.mapView().setScene(levels[newLevel].getView())
            scene = self.__registry.mainWindow.mapView().scene().getModel()
            #print scene

    def goLevelDown(self):
        return self.switchLevel(self.__registry.currentLevel.getMapIndex() - 1)

    def goLevelUp(self):
        return self.switchLevel(self.__registry.currentLevel.getMapIndex() + 1)

    def removeRoom(self):
        currentScene = self.__registry.currentLevel.getView()
        items = currentScene.selectedItems()
        for item in items:
            if isinstance(item, Room):
                #print 'deleting'
                item.getModel().delete()
            elif isinstance(item, view.Label):
                item.scene().removeItem(item)


    def enableCreation(self, enable):
        self.__enableCreation = bool(enable)

    def enableAutoPlacement(self, enable):
        self.__enableAutoPlacement = bool(enable)

    def goUp(self):
        #print 'goUp'
        return self.goFromActive(Direction.U, Direction.D)

    def goDown(self):
        #print 'goDown'
        return self.goFromActive(Direction.D, Direction.U)

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

    def     goWest(self):
        return self.goFromActive(Direction.W, Direction.E)

    def goNorthWest(self):
        return self.goFromActive(Direction.NW, Direction.SE)

    def goFromActive(self, fromExit, toExit):
        if self.__registry.currentlyVisitedRoom is None:
            return QtGui.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtGui.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        return self.go(currentRoom, fromExit, toExit)

    def dropRoomFromShadow(self):
        if self.__registry.currentlyVisitedRoom is None:
            self.__registry.roomShadow.stopProcess()
            return QtGui.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtGui.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom
        fromExit = self.__registry.roomShadow.exitBy()
        toExit = self.__registry.roomShadow.entryBy()
        dropAtPoint = self.__registry.roomShadow.pos()

        if currentRoom.getView().pos() == dropAtPoint:
            self.__registry.roomShadow.stopProcess()
            return

        destinationRoom=None

        #collision check at new point
        for item in currentRoom.getView().scene().items(self.__coordinatesHelper.getSelectionAreaFromPoint(dropAtPoint)):
            if isinstance(item, view.Room):
                destinationRoom = item
                break

        if destinationRoom is not None:
            if(destinationRoom.getModel().hasExit(toExit)):
                self.__registry.roomShadow.stopProcess()
                return QtGui.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is already an exit at entry direction from destination room', QtGui.QMessageBox.Ok)

            destinationRoom.getModel().addExit(toExit)
            self.markVisitedRoom(destinationRoom.getModel())
            newRoom = destinationRoom.getModel()
        else:
            newRoom = self.__roomFactory.createAt(dropAtPoint, currentRoom.getView().scene())
            newRoom.addExit(toExit)
            self.markVisitedRoom(newRoom)

        currentRoom.addExit(fromExit)
        self.__roomFactory.linkRooms(currentRoom, fromExit, newRoom, toExit, currentRoom.getView().scene())

        self.__registry.mainWindow.autoPlacement.setCheckState(QtCore.Qt.Checked)

    def goCustom(self, direction):
        if self.__registry.currentlyVisitedRoom is None:
            return QtGui.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtGui.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        #let's check for masked exists first
        for exit_, link in currentRoom.getLinks().items():
            #print link.getSourceSideFor(currentRoom)[2]
            pass

        #still here? then maybe a custom link?
        for link in currentRoom.getCustomLinks():
            sourceSide = link.getSourceSideFor(currentRoom)
            if sourceSide[2] is not None and sourceSide[2] == direction:
                return self.markVisitedRoom(link.getDestinationFor(currentRoom))


    def go(self, currentRoom, fromExit, toExit):

        """
        To refactor this horrors
        Think about a proper navigator that can accept any object type and move it on the grid using coordinatesHelper
         this class should not be responsible for any room creation / collision check
        """
        if currentRoom.hasExit(fromExit) and (not self.__enableCreation or self.__enableAutoPlacement):
            """
            @todo: This has to be changed when exit links are operational to use links rather than positions
            """

            exitLink = currentRoom.linkAt(fromExit)
            #print exitLink
            destinationRoom = exitLink.getDestinationFor(currentRoom)
            self.markVisitedRoom(destinationRoom)

            #if destinationRoom.getLevel().getId() != currentRoom.getLevel().getId():
            #    if fromExit == Direction.U: self.goLevelUp()
            #    elif fromExit == Direction.D: self.goLevelDown()

        elif (self.__enableCreation):

            if fromExit in [Direction.U, Direction.D] or toExit in [Direction.D, Direction.U]:
                #print 'creating multilevel room'
                #what happens when changing level?
                #if create mode check for collision and if no create ate the same coordinates but on different scene
                otherLevelIndex = self.__registry.currentLevel.getMapIndex()
                otherLevelIndex += 1 if fromExit == Direction.U else -1
                levels = self.__map.levels()
                otherLevel = levels[otherLevelIndex] if otherLevelIndex in levels else self.__roomFactory.spawnLevel(otherLevelIndex)

                destinationRoom = otherLevel.getView().itemAt(currentRoom.getView().pos())

                if destinationRoom is not None:
                    newRoom = destinationRoom.getModel()
                else:
                    newRoom = self.__roomFactory.createAt(currentRoom.getView().pos(), otherLevel.getView())

                currentRoom.addExit(fromExit)
                newRoom.addExit(toExit)

                self.markVisitedRoom(newRoom)

                #if fromExit == Direction.U: self.goLevelUp()
                #else: self.goLevelDown()

                self.__roomFactory.linkRoomsBetweenLevels(currentRoom, fromExit, newRoom, toExit)

                return

            """
            if auto placement is enabled, we will simply place a room on the map, but if it is disabled
            we need to use something like a mask model that can be moved around the map and placed by
            hitting the keypad5 key, this should allow for custom linkage between rooms
            """

            destinationRoom=None
            destinationPoint = self.__coordinatesHelper.movePointInDirection(currentRoom.getView().pos(), fromExit)
            for item in currentRoom.getView().scene().items(self.__coordinatesHelper.getSelectionAreaFromPoint(destinationPoint)):
                if isinstance(item, view.Room):
                    destinationRoom = item
                    break

            if not self.__enableAutoPlacement:
                roomShadow = self.__registry.roomShadow
                shadowLink = self.__registry.shadowLink
                if not roomShadow.inProcess():
                    if currentRoom.getView().scene() is not roomShadow.scene():
                        currentRoom.getView().scene().addItem(roomShadow)
                        currentRoom.getView().scene().addItem(shadowLink)
                    if destinationRoom is not None:
                        pass
                    else:
                        newPosition = self.__coordinatesHelper.movePointInDirection(currentRoom.getView().pos(), fromExit)
                        roomShadow.setPos(newPosition)

                    roomShadow.setVisible(True)
                    shadowLink.setVisible(True)
                    roomShadow.setInProcess(True)
                    roomShadow.setExitBy(fromExit)
                    roomShadow.setEntryBy(toExit)
                    shadowLink.redraw()
                else:
                    newPosition = self.__coordinatesHelper.movePointInDirection(roomShadow.pos(), fromExit)
                    roomShadow.setPos(newPosition)
                    roomShadow.setEntryBy(toExit)
                    shadowLink.redraw()
            else:

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

    def mergeRooms(self, existingRoom, overlappingRoom):
        print 'running room merge for'
        print existingRoom
        print overlappingRoom
        for exit, link in existingRoom.getLinks().items():
            if overlappingRoom.hasExit(exit):
                raise Exception('Cannot merge rooms as some exits are overlapping')

        #we will delete the old room cause new one is half way through update event so we don't want to screw with it
        links = existingRoom.getLinks()
        for exit_, link in links.items():
            link.replaceRoomPointer(existingRoom, overlappingRoom)
            existingRoom.removeExit(exit_)
            overlappingRoom.addExit(exit_)
            overlappingRoom.addLink(exit_, link)
            link.getView().redraw()

        overlappingRoom.getView().update()

        existingRoom.delete()

    def markVisitedRoom(self, roomModel):
        if self.__registry.currentlyVisitedRoom is not None:
            self.__registry.previouslyVisitedRoom = self.__registry.currentlyVisitedRoom
            self.__registry.currentlyVisitedRoom.setCurrentlyVisited(False)
            self.__registry.currentlyVisitedRoom.getView().update()

        self.__registry.currentlyVisitedRoom = roomModel

        roomModel.setCurrentlyVisited(True)
        roomModel.getView().clearFocus()

        if len(roomModel.getView().scene().views()):
            #workaround to a bug with centerAt
            roomModel.getView().setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            roomModel.getView().scene().views()[0].centerOn(roomModel.getView().pos())
            roomModel.getView().setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
            pass

        for item in roomModel.getView().scene().selectedItems():
            item.setSelected(False)

        roomModel.getView().setPos(roomModel.position())
        roomModel.getView().update()

        self.switchLevel(roomModel.getLevel().getMapIndex())
        self.__registry.mainWindow.roomIdDisplay.setText(roomModel.getId())
        self.__properties.updatePropertiesFromRoom(roomModel)
        if len(roomModel.getProperty(Room.PROP_COMMANDS)):
            if  hasattr(self.__registry, 'connection'):
                self.__registry.connection.send(roomModel.getProperty(Room.PROP_COMMANDS)+'\n')



class Clipboard:
    def copyRooms(self, scene, QRectF):
        items = []
        idMap = {}
        for item in scene.selectedItems():
            pos = item.sceneBoundingRect()
            x = pos.x()-QRectF.x()
            y = pos.y()-QRectF.y()
            id_ = str(uuid.uuid1())
            idMap[item.getModel().getId()] = id_
            item = (x,y, id_)
            items.append(item)

        links = []
        for item in scene.selectedItems():
            for exit, link in item.getModel().getLinks().items():
                if link.getLeft()[0].getId() not in idMap: continue
                if link.getRight()[0].getId() not in idMap: continue
                #we now know the link is within selection
                links.append([idMap[link.getLeft()[0].getId()],link.getLeft()[1],idMap[link.getRight()[0].getId()],link.getRight()[1]])


        data = {'rooms':items, 'links':links}
        QtGui.QApplication.clipboard().setText(base64.standard_b64encode(json.dumps(data)))










