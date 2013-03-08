__author__ = 'thornag'

import json, zlib
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
        #levelsData = base64.standard_b64encode(json.dumps(levels))
        levelsData = levels
        print 'Done -----'

        rooms = []
        print 'Gathering rooms'
        for index, room in mapObject.rooms().items():
            print room.getSettings()
            rooms.append([room.getId(), room.getLevel().getId(), room.getView().pos().x(), room.getView().pos().y(), room.getSettings()])
        print 'Serializing rooms'
        #roomsData = base64.standard_b64encode(json.dumps(rooms))
        roomsData = rooms
        print 'Done -----'

        customLinksSource = []

        links = []
        print 'Gathering links'
        for index, link in mapObject.links().items():
            if link.isCustom():
                customLinksSource.append(link)
                continue
            links.append([link.getLeft()[0].getId(), link.getLeft()[1], link.getLeft()[2], link.getRight()[0].getId(), link.getRight()[1], link.getRight()[2]])
        print 'Serializing links'
        #linksData = base64.standard_b64encode(json.dumps(links))
        linksData = links
        print 'Done -----'

        customLinks = []
        print 'Gathering custom links'
        for link in customLinksSource:
            customLinks.append([link.getLeft()[0].getId(), link.getLeft()[1], link.getLeft()[2], link.getRight()[0].getId(), link.getRight()[1], link.getRight()[2]])
        print 'Serializing links'
        #linksData = base64.standard_b64encode(json.dumps(links))
        customLinksData = customLinks
        print 'Done -----'

        print 'Creating data dictionary'
        fileData = dict([('levels', levelsData),('rooms', roomsData), ('links', linksData), ('customLinks', customLinksData)])

        print 'Serializing it'
        fileData = base64.standard_b64encode(json.dumps(fileData))

        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper/'
        mapFile = baseDir+Serializer.mapFile

        try:
            os.mkdir(baseDir)
        except OSError as e:
            if(e.errno != 17):
                raise e

        if os.path.exists(mapFile):
            shutil.move(mapFile, mapFile+'.bak')

        fileData = zlib.compress(fileData)

        print 'Writing data dictionary'
        f = open(mapFile, 'wb')
        f.write(fileData)
        f.close()

        print ' ------ SAVE COMPLETE -------'

    @staticmethod
    def loadMap(mapView):
        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper/'
        mapFile = baseDir+Serializer.mapFile

        try:
            f = open(mapFile, 'rb')
        except: return False

        mapData = f.read()

        f.close()

        try:
            mapData = zlib.decompress(mapData)
        except: pass

        try:
            mapData = json.loads(base64.standard_b64decode(mapData))
        except: return False

        if isinstance(mapData['levels'], basestring):
            levels = json.loads(base64.standard_b64decode(mapData['levels']))
            rooms = json.loads(base64.standard_b64decode(mapData['rooms']))
            links = json.loads(base64.standard_b64decode(mapData['links']))
            customLinks = []
        else:
            levels = mapData['levels']
            rooms = mapData['rooms']
            links = mapData['links']
            try:
                customLinks = mapData['customLinks']
            except: customLinks = []

        factory = Serializer.factory

        from PyQt4 import QtCore

        levelsById = {}

        for level in levels:
            levelModel = factory.spawnLevel(level[1], level[0])
            levelModel.getView().setSceneRect(QtCore.QRectF(level[2], level[3], level[4], level[5]))
            levelsById[levelModel.getId()] = levelModel

        if not len(Serializer.registry.levels()): return False

        for room in rooms:
            roomModel = factory.createAt(QtCore.QPointF(room[2], room[3]), levelsById[room[1]].getView(), room[0], room[4])

        mapView.setScene(Serializer.registry.levels()[0].getView())

        rooms = Serializer.registry.rooms()

        links =  links + customLinks

        for link in links:
            if len(link) == 4:
                leftRoom, leftExit = link[:2]
                rightRoom, rightExit = link[2:]
                leftExitLabel = rightExitLabel = None
            else:
                leftRoom, leftExit, leftExitLabel = link[:3]
                rightRoom, rightExit, rightExitLabel = link[3:]

            if leftRoom not in rooms or rightRoom not in rooms: continue
            leftRoom = rooms[str(leftRoom)]
            rightRoom = rooms[str(rightRoom)]

            leftRoom.addExit(leftExit)
            rightRoom.addExit(rightExit)

            isUpDown = leftExit in [model.Direction.U, model.Direction.D] or rightExit in [model.Direction.U, model.Direction.D]

            if leftRoom.getLevel().getId() == rightRoom.getLevel().getId() and not isUpDown:
                factory.linkRooms(leftRoom, leftExit, rightRoom, rightExit, levelsById[rightRoom.getLevel().getId()].getView(), leftExitLabel, rightExitLabel)
            else:
                factory.linkRoomsBetweenLevels(leftRoom, leftExit, rightRoom, rightExit)

        return True
