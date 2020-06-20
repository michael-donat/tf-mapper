import di, view
import math, uuid
from .entity import *
from PyQt5 import QtCore, QtGui, QtWidgets
import json, base64

__author__ = 'thornag'

class Zone:
    __name=None
    __levels=None
    __id=None
    def __init__(self, name, id=None):
        self.__name=name
        self.__levels={}
        self.__id = str(id)
    def registerLevel(self, levelObject):
        self.__levels[levelObject.getMapIndex()] = levelObject
    def getLevelByIndex(self, levelIndex):
        return self.__levels[levelIndex]
    def levelByIndexExists(self, levelIndex):
        return levelIndex in self.__levels.keys()
    def id(self):
        return self.__id
    def name(self):
        return self.__name
    def setName(self, name):
        self.__name = name

class Map:
    __rooms={}
    __levels={}
    __links={}
    __zones={}
    __path=[]
    __currentZone=None

    def getPath(self):
        return self.__path

    def setPath(self, path):
        self.__path = path

    def clear(self):
        for evel in self.__levels:
            self.__levels[evel].getView().clear()
        self.__rooms={}
        self.__levels={}
        self.__links={}
        self.__zones={}
        self.__currentZone=None

    def currentZone(self):
        return self.__currentZone

    def setCurrentZone(self, zoneId):
        self.__currentZone = self.__zones[str(zoneId)]

    def levels(self):
        return self.__levels

    def getLevelByIndex(self, levelIndex):
        return self.currentZone().getLevelByIndex(levelIndex)

    def levelExists(self, levelIndex):
        return self.currentZone().levelByIndexExists(levelIndex)

    def getZeroLevel(self):
        return self.getLevelByIndex(0)

    def getZoneById(self, zoneId):
        return self.__zones[zoneId]

    def getRoomById(self, id):
        if id in self.__rooms:
            return self.__rooms[id]

    def rooms(self):
        return self.__rooms

    def links(self):
        return self.__links

    def zones(self):
        return self.__zones

    def registerZone(self, zone):
        self.__zones[zone.id()] = zone

    def registerRoom(self, room):
        self.__rooms[room.getId()] = room

    def registerLevel(self, level):
        self.__levels[level.getId()] = level

    def removeRoom(self, room):
        del self.__rooms[room.getId()]

    def registerLink(self, link):
        self.__links[link.getId()] = link

    def removeLink(self, link):
        if link.getId() in self.__links:
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
    def getAllAsList():
        return [Direction.N, Direction.NE, Direction.E, Direction.SE, Direction.S, Direction.SW, Direction.W, Direction.NW, Direction.D, Direction.U, Direction.OTHER]

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
        if exit == Direction.U: return 'UP'
        if exit == Direction.D: return 'DN'
        if exit == Direction.OTHER: return 'X'


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
        if direction in [Direction.OTHER, Direction.U, Direction.D]:
            newPosition = QPoint + QtCore.QPointF(midPoint, midPoint)

        return newPosition

    def getExitPoint(self, exitDescription):
        room, direction, label, rebind = exitDescription

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
            self.createAt(QtCore.QPointF(QPoint.x()+room[0],QPoint.y()+room[1]), QGraphicsScene, room[2], room[3])
        rooms = self.__map.rooms()
        for link in data['links']:
            leftRoom, leftExit, leftLabel, leftRebind = link[:4]
            rightRoom, rightExit, rightLabel, rightRebind = link[4:]
            if leftRoom not in rooms or rightRoom not in rooms: continue
            leftRoom = rooms[str(leftRoom)]
            rightRoom = rooms[str(rightRoom)]

            leftRoom.addExit(leftExit)
            rightRoom.addExit(rightExit)

            self.linkRooms(leftRoom, leftExit, rightRoom, rightExit, QGraphicsScene, leftLabel, rightLabel, leftRebind, rightRebind)

    def createLabelAt(self, QPoint, QGraphicsScene, labeltext='LABEL'):
        text = view.Label(labeltext)
        QGraphicsScene.addItem(text)
        text.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsFocusable | QtWidgets.QGraphicsItem.ItemIsMovable);
        text.setPos(QtCore.QPointF(QPoint))

    def createAt(self, QPoint, QGraphicsScene, Id=None, properties=None):
        if properties is None:
            properties={}
            properties[Room.PROP_COLOR] = self.__registry.defColor
            properties[Room.PROP_CLASS] = str(self.__registry.defClass)
        room = self.spawnRoom(Id, properties)
        QGraphicsScene.addItem(room.getView())
        room.setPosition(QPoint)
        boundingRect = QGraphicsScene.sceneRect();
        """boundingRect = QGraphicsScene.itemsBoundingRect()"""
        if((QPoint.x() - 50) < boundingRect.left() or (QPoint.x() + 50) > boundingRect.right() or (QPoint.y() - 50) < boundingRect.top() or (QPoint.y() + 50) > boundingRect.bottom()):
            boundingRect.adjust(-100,-100,100,100)
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
        #print(isCustomLink)
        link = Link() if not isCustomLink else CustomLink()
        id_ = uuid.uuid1() if id==None else id
        link.setId(id_)
        self.__map.registerLink(link)
        if(linkLess): return link
        viewLink = view.Link()
        link.setView(viewLink)
        return link

    def linkRoomsBetweenLevels(self, leftRoom, leftExit, rightRoom, rightExit, leftExitLabel=None, rightExitLabel=None, leftExitRebind=None, rightExitRebind=None):
        return self.linkRooms(leftRoom, leftExit, rightRoom, rightExit, None, leftExitLabel, rightExitLabel, leftExitRebind, rightExitRebind)


    def linkRooms(self, leftRoom, leftExit, rightRoom, rightExit, QGraphicsScene=None, leftLinkCustomLabel=None, rightLinkCustomLabel=None, leftLinkRebind=None, rightLinkRebind=None):
        #need to validate first
        if(Direction.OTHER != leftExit and leftRoom.hasLinkAt(leftExit)): # and not leftRoom.linkAt(leftExit).pointsAt(rightRoom)):
            raise Exception('Left room already links somewhere through given exit')

        if(Direction.OTHER != rightExit and rightRoom.hasLinkAt(rightExit)): # and not rightRoom.linkAt(rightExit).pointsAt(leftRoom)):
            raise Exception('Right room already links somewhere through given exit')

        #good to link
        link = self.spawnLink(QGraphicsScene is None, None, Direction.OTHER in [leftExit, rightExit])
        link.setLeft(leftRoom, leftExit, leftLinkCustomLabel, leftLinkRebind)
        link.setRight(rightRoom, rightExit, rightLinkCustomLabel, rightLinkRebind)
        leftRoom.addLink(leftExit, link)
        rightRoom.addLink(rightExit, link)

        if QGraphicsScene is None: return

        link.getView().redraw()
        QGraphicsScene.addItem(link.getView())

        return link

    def spawnZone(self, name, id=None):
        id_ = uuid.uuid1() if id==None else id
        zone = Zone(name, id_)
        self.__map.registerZone(zone)
        return zone

    def spawnLevel(self, mapIndex, id=None, zone=None):
        if zone is None:
            zone = self.__map.currentZone().id()

        level = Level(mapIndex)
        id_ = uuid.uuid1() if id==None else id
        level.setId(id_)
        level.setZone(zone)
        viewLevel = view.uiMapLevel()
        viewLevel.setBackgroundBrush(QtGui.QColor(217, 217, 217))
        level.setView(viewLevel)
        self.__map.registerLevel(level)
        self.__map.getZoneById(zone).registerLevel(level)
        return level


class Registry:
    currentlyVisitedRoom=None
    roomShadow=None
    defColor=None
    defClass=None
    centerAt=True
    applyColors=True
    applyClasses=True
    def __init__(self):
        self.__rooms=[]

    def reinit(self):
        self.currentlyVisitedRoom=None
        self.__rooms=[]


    def setCenterAt(self, Center=True):
        self.centerAt = Center

    def setDefaultClass(self, roomClass):
        self.defClass = roomClass

    def setDefaultColor(self, color):
        if isinstance(color, QtGui.QColor):
            color = color.name()
        if not len(color): self.defColor=None
        else: self.defColor=str(color)


class Navigator(QtCore.QObject):
    _lastCreatedRoom = None
    _lastCreatedLink = None
    roomSelectedSignal=QtCore.pyqtSignal(object)
    __map=di.ComponentRequest('Map')
    __config=di.ComponentRequest('Config')
    __registry=di.ComponentRequest('Registry')
    __roomFactory=di.ComponentRequest('RoomFactory')
    __coordinatesHelper=di.ComponentRequest('CoordinatesHelper')
    __enableCreation=False
    __enableAutoPlacement=True
    __enableSameUpDown=True
    __properties=di.ComponentRequest('Properties')
    def __init__(self):
        super(Navigator, self).__init__()

    def changeZone(self, zone):
        self.__map.setCurrentZone(zone)

    def switchLevel(self, newLevel):
        levels = self.__map.levels()
        if self.__map.levelExists(newLevel):
            level = self.__map.getLevelByIndex(newLevel)
            if self.__registry.currentLevel is level:
                return

            newView = level.getView()
            view = self.__registry.currentLevel.getView().views()[0]
            center = view.mapToScene(view.rect().center())
            self.__registry.mainWindow.mapView().setScene(self.__map.getLevelByIndex(newLevel).getView())
            scene = self.__registry.mainWindow.mapView().scene().getModel()
            view.centerOn(center)
            #print(scene)

    def goLevelDown(self):
        return self.switchLevel(self.__registry.currentLevel.getMapIndex() - 1)

    def goLevelUp(self):
        return self.switchLevel(self.__registry.currentLevel.getMapIndex() + 1)

    def removeRoom(self):
        currentScene = self.__registry.currentLevel.getView()
        items = currentScene.selectedItems()
        for item in items:
            if isinstance(item, view.Room):
                item.getModel().delete()
            elif isinstance(item, view.Label):
                item.scene().removeItem(item)


    def enableCreation(self, enable):
        self.__enableCreation = bool(enable)
        if  hasattr(self.__registry, 'connection'):
            if enable:
                self.__registry.connection.send('map:mode:create\n')
            else:
                self.__registry.connection.send('map:mode:walk\n')

    def enableSameUpDown(self, enable):
        self.__enableSameUpDown = bool(enable)

    def enableAutoPlacement(self, enable):
        self.__enableAutoPlacement = bool(enable)

    def goUp(self):
        #print('goUp')
        return self.goFromActive(Direction.U, Direction.D)

    def goDown(self):
        #print('goDown')
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
            return QtWidgets.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtWidgets.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        return self.go(currentRoom, fromExit, toExit)

    def dropRoomFromShadow(self):
        if self.__registry.currentlyVisitedRoom is None:
            self.__registry.roomShadow.stopProcess()
            return QtWidgets.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtWidgets.QMessageBox.Ok)

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
                return QtWidgets.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is already an exit at entry direction from destination room', QtWidgets.QMessageBox.Ok)

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

    def goFollow(self, direction):
        if self.__registry.currentlyVisitedRoom is None:
            return QtWidgets.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtWidgets.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        #let's check for masked exists first
        for exit_, link in currentRoom.getLinks().items():
            sourceSide = link.getSourceSideFor(currentRoom)
            if sourceSide[2] is not None and sourceSide[2] == direction:
                return self.markVisitedRoom(link.getDestinationFor(currentRoom))
                #print(link.getSourceSideFor(currentRoom)[2])
            pass

        #still here? then maybe a custom link?
        for link in currentRoom.getCustomLinks():
            sourceSide = link.getSourceSideFor(currentRoom)
            if sourceSide[2] is not None and sourceSide[2] == direction:
                return self.markVisitedRoom(link.getDestinationFor(currentRoom))

    def goCustom(self, direction):
        if self.__registry.currentlyVisitedRoom is None:
            return QtWidgets.QMessageBox.question(self.__registry.mainWindow, 'Alert', 'There is no active room selected', QtWidgets.QMessageBox.Ok)

        currentRoom = self.__registry.currentlyVisitedRoom

        #let's check for masked exists first
        for exit_, link in currentRoom.getLinks().items():
            sourceSide = link.getSourceSideFor(currentRoom)
            if sourceSide[3] is not None and len(sourceSide[3]) and sourceSide[3] == direction:
                return self.markVisitedRoom(link.getDestinationFor(currentRoom))
            #print(link.getSourceSideFor(currentRoom)[2])
            pass

        #still here? then maybe a custom link?
        for link in currentRoom.getCustomLinks():
            sourceSide = link.getSourceSideFor(currentRoom)
            if sourceSide[3] is not None and len(sourceSide[3]) and sourceSide[3] == direction:
                return self.markVisitedRoom(link.getDestinationFor(currentRoom))


    def go(self, currentRoom, fromExit, toExit):

        self._lastCreatedRoom = None
        self._lastCreatedLink = None

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

            if exitLink.getSourceSideFor(currentRoom)[3] is not None: return

            #print(exitLink)
            destinationRoom = exitLink.getDestinationFor(currentRoom)
            self.markVisitedRoom(destinationRoom)

            #if destinationRoom.getLevel().getId() != currentRoom.getLevel().getId():
            #    if fromExit == Direction.U: self.goLevelUp()
            #    elif fromExit == Direction.D: self.goLevelDown()

        elif (self.__enableCreation and not self.__registry.blockCreation):

            if not self.__enableSameUpDown and (fromExit in [Direction.U, Direction.D] or toExit in [Direction.D, Direction.U]):
                #print('creating multilevel room')
                #what happens when changing level?
                #if create mode check for collision and if no create ate the same coordinates but on different scene
                otherLevelIndex = self.__registry.currentLevel.getMapIndex()
                otherLevelIndex += 1 if fromExit == Direction.U else -1

                if self.__map.levelExists(otherLevelIndex):
                    otherLevel = self.__map.getLevelByIndex(otherLevelIndex)
                else:
                    otherLevel = self.__roomFactory.spawnLevel(otherLevelIndex)

                destinationRoom = otherLevel.getView().itemAt(currentRoom.getView().pos())

                if destinationRoom is not None:
                    newRoom = destinationRoom.getModel()
                else:
                    newRoom = self.__roomFactory.createAt(currentRoom.getView().pos(), otherLevel.getView())
                    self._lastCreatedRoom = newRoom

                currentRoom.addExit(fromExit)
                newRoom.addExit(toExit)

                self.markVisitedRoom(newRoom)

                #if fromExit == Direction.U: self.goLevelUp()
                #else: self.goLevelDown()

                self._lastCreatedLink = self.__roomFactory.linkRoomsBetweenLevels(currentRoom, fromExit, newRoom, toExit)

                return

            """
            if auto placement is enabled, we will simply place a room on the map, but if it is disabled
            we need to use something like a mask model that can be moved around the map and placed by
            hitting the keypad5 key, this should allow for custom linkage between rooms
            """

            destinationRoom=None
            if not (fromExit in [Direction.U, Direction.D] or toExit in [Direction.D, Direction.U]):
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

                fromExitDirection = fromExit

                if self.__enableSameUpDown and (fromExit in [Direction.U, Direction.D] or toExit in [Direction.D, Direction.U]):
                    newRoomDirectionUD = None
                    for tryPlacement in [Direction.N, Direction.NE, Direction.E, Direction.SE, Direction.S, Direction.SW, Direction.W, Direction.NW]:
                        destinationPoint = self.__coordinatesHelper.movePointInDirection(currentRoom.getView().pos(), tryPlacement)
                        newRoomDirectionUD = tryPlacement
                        for item in currentRoom.getView().scene().items(self.__coordinatesHelper.getSelectionAreaFromPoint(destinationPoint)):
                            if isinstance(item, view.Room):
                                newRoomDirectionUD = None
                                break
                        if newRoomDirectionUD is not None:
                            break
                    if newRoomDirectionUD is None:
                        return

                    fromExitDirection = newRoomDirectionUD

                if destinationRoom is not None:
                    destinationRoom.getModel().addExit(toExit)
                    self.markVisitedRoom(destinationRoom.getModel())
                    newRoom = destinationRoom.getModel()
                else:
                    newRoom = self.__roomFactory.createInDirection(fromExitDirection, currentRoom.getView().pos(), currentRoom.getView().scene())
                    self._lastCreatedRoom = newRoom
                    newRoom.addExit(toExit)
                    self.markVisitedRoom(newRoom)


                self._lastCreatedLink = link = self.__roomFactory.linkRooms(currentRoom, fromExit, newRoom, toExit, currentRoom.getView().scene())
                """
                @todo: Need to refactor this so navigator doesnt create set active
                """

    def undoCreation(self):

        if self._lastCreatedRoom is not None or self._lastCreatedLink is not None:
            if self.__registry.previouslyVisitedRoom is not None:
                roomId = self.__registry.previouslyVisitedRoom.getId()
                roomId = str(roomId)
                if roomId not in self.__map.rooms().keys(): return False
                room = self.__map.rooms()[roomId]
                self.markVisitedRoom(room)

        if self._lastCreatedRoom is not None:
            self._lastCreatedRoom.delete()
            self._lastCreatedRoom = None
            self._lastCreatedLink = None

        if self._lastCreatedLink is not None:
            self._lastCreatedLink.getLeft()[0].deleteLink(self._lastCreatedLink)
            self._lastCreatedRoom = None
            self._lastCreatedLink = None


    def mergeRooms(self, existingRoom, overlappingRoom):
        print('running room merge for')
        print(existingRoom)
        print(overlappingRoom)
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

    def viewRoom(self, roomId):
        roomId = str(roomId)
        if roomId not in self.__map.rooms().keys(): return False
        roomModel = self.__map.rooms()[roomId]

        self.changeZone(roomModel.getLevel().zone())
        self.switchLevel(roomModel.getLevel().getMapIndex())

        roomModel.getView().setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        roomModel.getView().scene().views()[0].centerOn(roomModel.getView().pos())
        roomModel.getView().setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)


    def markVisitedRoom(self, roomModel):
        if self.__registry.currentlyVisitedRoom is not None:
            self.__registry.previouslyVisitedRoom = self.__registry.currentlyVisitedRoom
            self.__registry.currentlyVisitedRoom.setCurrentlyVisited(False)
            self.__registry.currentlyVisitedRoom.getView().update()

        self.__registry.currentlyVisitedRoom = roomModel

        roomModel.setCurrentlyVisited(True)
        roomModel.getView().clearFocus()

        self.changeZone(roomModel.getLevel().zone())
        self.switchLevel(roomModel.getLevel().getMapIndex())

        if len(roomModel.getView().scene().views()):
            if self.__registry.centerAt:
                #workaround to a bug with centerAt
                roomModel.getView().setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                roomModel.getView().scene().views()[0].centerOn(roomModel.getView().pos())
                roomModel.getView().setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
                pass
            else:
                roomPositionWithinScene = roomModel.getView().pos()
                roomPositionWithinView = roomModel.getView().scene().views()[0].mapFromScene(roomPositionWithinScene)
                if roomPositionWithinView.x() < 10 or roomPositionWithinView.y() < 10:
                    roomModel.getView().setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                    roomModel.getView().scene().views()[0].centerOn(roomModel.getView().pos())
                    roomModel.getView().setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)


        for item in roomModel.getView().scene().selectedItems():
            item.setSelected(False)

        roomModel.getView().setPos(roomModel.position())
        roomModel.getView().update()

        for i in range(0, self.__registry.mainWindow.selectZone.count()):
            if self.__registry.mainWindow.selectZone.itemData(i) == roomModel.getLevel().zone():
                self.__registry.mainWindow.selectZone.blockSignals(True)
                self.__registry.mainWindow.selectZone.setCurrentIndex(i)
                self.__registry.mainWindow.selectZone.blockSignals(False)

        self.__registry.mainWindow.roomIdDisplay.setText(roomModel.getId())
        self.__properties.updatePropertiesFromRoom(roomModel)

        if  hasattr(self.__registry, 'connection'):
            self.__registry.connection.send('room:enter\n')
            self.__registry.connection.send('room:id:%s\n' % roomModel.getId())

        if len(roomModel.getProperty(Room.PROP_COMMANDS)):
            if  hasattr(self.__registry, 'connection'):
                self.__registry.connection.send(roomModel.getProperty(Room.PROP_COMMANDS)+'\n')

        if  hasattr(self.__registry, 'connection'):
            if roomModel.hasMaskedExits():
                self.__registry.connection.send(roomModel.getMaskedExitsString())






class Clipboard:
    def copyRooms(self, scene, QRectF):
        items = []
        idMap = {}
        linkIdMap = []
        for item in scene.selectedItems():
            pos = item.sceneBoundingRect()
            x = pos.x()-QRectF.x()
            y = pos.y()-QRectF.y()
            id_ = str(uuid.uuid1())
            idMap[item.getModel().getId()] = id_
            item = (x,y, id_, item.getModel().getSettings())
            items.append(item)

        links = []
        for item in scene.selectedItems():
            for exit, link in item.getModel().getLinks().items():
                if link.getLeft()[0].getId() not in idMap: continue
                if link.getRight()[0].getId() not in idMap: continue
                if link.getId() in linkIdMap: continue
                linkIdMap.append(link.getId())
                #we now know the link is within selection
                leftLink = link.getLeft()
                links.append([idMap[link.getLeft()[0].getId()],link.getLeft()[1],link.getLeft()[2],link.getLeft()[3],idMap[link.getRight()[0].getId()],link.getRight()[1],link.getRight()[2],link.getRight()[3]])


        data = {'rooms':items, 'links':links}
        QtWidgets.QApplication.clipboard().setText(json.dumps(data))
