__author__ = 'thornag'

import json
import base64
import textwrap, string
import os, shutil, sys
import model.model as model

import di

class Serializer:
    factory = di.ComponentRequest('RoomFactory')
    registry = di.ComponentRequest('Map')
    mapFile=None
    @staticmethod
    def saveMap(fileLocation, mapObject):
        levels = []
        print 'Gathering levels'
        for index, level in mapObject.levels().items():
            levels.append([level.getId(), level.getMapIndex(), level.getView().sceneRect().x(),level.getView().sceneRect().y(), level.getView().sceneRect().width(), level.getView().sceneRect().height()])
        print 'Serializing levels'
        levelsData = base64.standard_b64encode(json.dumps(levels))
        print 'Done -----'

        rooms = []
        print 'Gathering rooms'
        for index, room in mapObject.rooms().items():
            rooms.append([room.getId(), room.getLevel().getId(), room.getView().pos().x(), room.getView().pos().y(), room.getSettings()])
        print 'Serializing rooms'
        roomsData = base64.standard_b64encode(json.dumps(rooms))
        print 'Done -----'

        links = []
        print 'Gathering rooms'
        for index, link in mapObject.links().items():
            links.append([link.getLeft()[0].getId(), link.getLeft()[1], link.getRight()[0].getId(), link.getRight()[1]])
        print 'Serializing rooms'
        linksData = base64.standard_b64encode(json.dumps(links))
        print 'Done -----'

        print 'Creating data dictionary'
        fileData = dict([('levels', levelsData),('rooms', roomsData), ('links', linksData)])

        print 'Serializing it'
        fileData = base64.standard_b64encode(json.dumps(fileData))

        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper'
        mapFile = baseDir+Serializer.mapFile

        try:
            os.mkdir(baseDir)
        except OSError as e:
            if(e.errno != 17):
                raise e

        if os.path.exists(mapFile):
            shutil.move(mapFile, mapFile+'.bak')

        print 'Writing data dictionary'
        f = open(mapFile, 'w')
        f.write(fileData+'\n')
        f.close()

        print ' ------ SAVE COMPLETE -------'

    @staticmethod
    def loadMap(mapView):
        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper'
        mapFile = baseDir+Serializer.mapFile

        try:
            f = open(mapFile, 'r')
        except: return False

        mapData = string.join(f.readlines(), '')
        f.close()

        try:
            mapData = json.loads(base64.standard_b64decode(mapData))
        except: return False

        levels = json.loads(base64.standard_b64decode(mapData['levels']))
        rooms = json.loads(base64.standard_b64decode(mapData['rooms']))
        links = json.loads(base64.standard_b64decode(mapData['links']))


        factory = Serializer.factory

        from PyQt4 import QtCore

        levelsById = {}

        for level in levels:
            levelModel = factory.spawnLevel(level[1], level[0])
            levelModel.getView().setSceneRect(QtCore.QRectF(level[2], level[3], level[4], level[5]))
            levelsById[levelModel.getId()] = levelModel

        if not len(Serializer.registry.levels()): return False


        for room in rooms:
            roomModel = factory.createAt(QtCore.QPointF(room[2], room[3]), levelsById[room[1]].getView(), room[0])

        mapView.setScene(Serializer.registry.levels()[0].getView())

        rooms = Serializer.registry.rooms()

        for link in links:
            leftRoom, leftExit = link[:2]
            rightRoom, rightExit = link[2:]
            if leftRoom not in rooms or rightRoom not in rooms: continue
            leftRoom = rooms[str(leftRoom)]
            rightRoom = rooms[str(rightRoom)]

            leftRoom.addExit(leftExit)
            rightRoom.addExit(rightExit)

            isUpDown = leftExit in [model.Direction.U, model.Direction.D] or rightExit in [model.Direction.U, model.Direction.D]

            if leftRoom.getLevel().getId() == rightRoom.getLevel().getId() and not isUpDown:
                factory.linkRooms(leftRoom, leftExit, rightRoom, rightExit, levelsById[rightRoom.getLevel().getId()].getView())
            else:
                factory.linkRoomsBetweenLevels(leftRoom, leftExit, rightRoom, rightExit)

        return True
