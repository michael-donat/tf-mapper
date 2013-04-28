__author__ = 'thornag'

import json, zlib
import base64
import textwrap, string
import os, shutil, sys
import model.model as model
import view

import di

class Serializer:
    factory = di.ComponentRequest('RoomFactory')
    registry = di.ComponentRequest('Map')
    mapFile=None
    @staticmethod
    def saveMap(fileLocation, mapObject):
        levels = []
        #print 'Gathering levels'
        for index, level in mapObject.levels().items():
            levels.append([level.getId(), level.getMapIndex(), level.getView().sceneRect().x(),level.getView().sceneRect().y(), level.getView().sceneRect().width(), level.getView().sceneRect().height()])
        #print 'Serializing levels'
        #levelsData = base64.standard_b64encode(json.dumps(levels))
        levelsData = levels
        #print 'Done -----'

        rooms = []
        #print 'Gathering rooms'
        for index, room in mapObject.rooms().items():
            newSettings = {}
            for key, value in room.getSettings().items():
                if value == 'None': value=None
                if value == 'False': value=False
                if value == 'True': value=True
                newSettings[key] = value
            rooms.append([room.getId(), room.getLevel().getId(), room.getView().pos().x(), room.getView().pos().y(), newSettings])
        #print 'Serializing rooms'
        #roomsData = base64.standard_b64encode(json.dumps(rooms))
        roomsData = rooms
        #print 'Done -----'

        customLinksSource = []

        links = []
        #print 'Gathering links'
        for index, link in mapObject.links().items():
            if link.isCustom():
                customLinksSource.append(link)
                continue
            links.append([link.getLeft()[0].getId(), link.getLeft()[1], link.getLeft()[2], link.getLeft()[3], link.getRight()[0].getId(), link.getRight()[1], link.getRight()[2], link.getRight()[3]])
        #print 'Serializing links'
        #linksData = base64.standard_b64encode(json.dumps(links))
        linksData = links
        #print 'Done -----'

        customLinks = []
        #print 'Gathering custom links'
        for link in customLinksSource:
            customLinks.append([link.getLeft()[0].getId(), link.getLeft()[1], link.getLeft()[2], link.getLeft()[3], link.getRight()[0].getId(), link.getRight()[1], link.getRight()[2], link.getRight()[3]])
        #print 'Serializing links'
        #linksData = base64.standard_b64encode(json.dumps(links))
        customLinksData = customLinks
        #print 'Done -----'

        labels = []
        for index, level in mapObject.levels().items():
            for item in level.getView().items():
                if isinstance(item, view.Label):
                    labels.append([item.x(), item.y(), level.getId(), str(item.toPlainText())])


        #print 'Creating data dictionary'
        mapData = fileData = dict([('levels', levelsData),('rooms', roomsData), ('links', linksData), ('customLinks', customLinksData), ('labels', labels)])

        #print 'Serializing it'
        fileData = base64.standard_b64encode(json.dumps(fileData))

        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper/'
        mapFile = baseDir+Serializer.mapFile

        if Serializer.mapFile[0] == '/':
            mapFile = Serializer.mapFile

        try:
            os.mkdir(baseDir)
        except OSError as e:
            if(e.errno != 17):
                raise e

        if os.path.exists(mapFile):
            shutil.move(mapFile, mapFile+'.bak')

        fileData = zlib.compress(fileData)

        #print 'Writing data dictionary'
        f = open(mapFile, 'wb')
        f.write(fileData)
        f.close()

        print 'Levels: %s' % len(mapData['levels'])
        print 'Rooms: %s' % len(mapData['rooms'])
        print 'Links: %s' % len(mapData['links'])
        print 'Labels: %s' % len(mapData['labels'])
        print 'Saved %s to %s ' % (Serializer.humanize_bytes(os.path.getsize(mapFile)), mapFile)

        #print ' ------ SAVE COMPLETE -------'

    @staticmethod
    def getHomeDir():
        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper/'
        return baseDir

    @staticmethod
    def loadMap(mapView, QProgressBar, application):

        if Serializer.mapFile is None:
            return

        import time
        def millis():
            return time.time() * 1000

        base = millis()

        print 'Start %s' % base

        baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
        baseDir = baseDir+'/.tf-mapper/'
        mapFile = baseDir+Serializer.mapFile

        if Serializer.mapFile[0] == '/':
            mapFile = Serializer.mapFile

        try:
            f = open(mapFile, 'rb')
        except: return False

        overall = (millis() - base)
        print 'File opened %s (%s)' % (overall, millis() - base)

        mapData = f.read()

        overall = (millis() - base)
        print 'File read %s (%s)' % (overall, millis() - overall)

        f.close()

        try:
            mapData = zlib.decompress(mapData)
        except: pass

        overall = (millis() - base)
        print 'File decompressed read %s (%s)' % (overall, millis() - overall)

        try:
            mapData = json.loads(base64.standard_b64decode(mapData))
        except: return False

        overall = (millis() - base)
        print 'File decoded %s (%s)' % (overall, millis() - overall)

        if isinstance(mapData['levels'], basestring):
            levels = json.loads(base64.standard_b64decode(mapData['levels']))
            rooms = json.loads(base64.standard_b64decode(mapData['rooms']))
            links = json.loads(base64.standard_b64decode(mapData['links']))
            customLinks = []
            labels=[]
        else:
            levels = mapData['levels']
            rooms = mapData['rooms']
            links = mapData['links']
            try:
                customLinks = mapData['customLinks']
            except: customLinks = []
            try:
                labels = mapData['labels']
            except: labels = []

        factory = Serializer.factory

        from PyQt4 import QtCore

        levelsById = {}

        for level in levels:
            levelModel = factory.spawnLevel(level[1], level[0])
            levelModel.getView().setSceneRect(QtCore.QRectF(level[2], level[3], level[4], level[5]))
            levelsById[levelModel.getId()] = levelModel

        overall = (millis() - base)
        print 'Levels created %s (%s)' % (overall, millis() - overall)

        QProgressBar.setValue(45)
        application.processEvents()

        if not len(Serializer.registry.levels()): return False

        for room in rooms:
            roomModel = factory.createAt(QtCore.QPointF(room[2], room[3]), levelsById[room[1]].getView(), room[0], room[4])

        overall = (millis() - base)
        print 'Rooms created %s (%s)' % (overall, millis() - overall)

        QProgressBar.setValue(55)
        application.processEvents()

        rooms = Serializer.registry.rooms()

        links =  links + customLinks

        for label in labels:
            factory.createLabelAt(QtCore.QPointF(label[0], label[1]), levelsById[label[2]].getView(), label[3])

        for link in links:
            if len(link) == 4:
                leftRoom, leftExit = link[:2]
                rightRoom, rightExit = link[2:]
                leftExitLabel = rightExitLabel = None
                leftExitRebind = rightExitRebind = None
            elif len(link) == 6:
                leftRoom, leftExit, leftExitLabel = link[:3]
                rightRoom, rightExit, rightExitLabel = link[3:]
                leftExitRebind = rightExitRebind = None
            else:
                leftRoom, leftExit, leftExitLabel, leftExitRebind = link[:4]
                rightRoom, rightExit, rightExitLabel, rightExitRebind = link[4:]

            if leftRoom not in rooms or rightRoom not in rooms: continue
            leftRoom = rooms[str(leftRoom)]
            rightRoom = rooms[str(rightRoom)]

            leftRoom.addExit(leftExit)
            rightRoom.addExit(rightExit)

            if leftExitLabel == 'None': leftExitLabel=None
            if rightExitLabel == 'None': rightExitLabel=None

            isUpDown = leftExit in [model.Direction.U, model.Direction.D] or rightExit in [model.Direction.U, model.Direction.D]

            try:
                if leftRoom.getLevel().getId() == rightRoom.getLevel().getId():
                    factory.linkRooms(leftRoom, leftExit, rightRoom, rightExit, levelsById[rightRoom.getLevel().getId()].getView(), leftExitLabel, rightExitLabel, leftExitRebind, rightExitRebind)
                else:
                    factory.linkRoomsBetweenLevels(leftRoom, leftExit, rightRoom, rightExit, leftExitRebind, rightExitRebind)
            except: pass

        overall = (millis() - base)
        print 'Links created %s (%s)' % (overall, millis() - overall)

        QProgressBar.setValue(65)
        application.processEvents()

        mapView.setScene(Serializer.registry.levels()[0].getView())

        overall = (millis() - base)
        print 'Completed created %s (%s)' % (overall, millis() - overall)

        return True

    @staticmethod
    def humanize_bytes(bytes, precision=1):
        abbrevs = (
            (1<<50L, 'PB'),
            (1<<40L, 'TB'),
            (1<<30L, 'GB'),
            (1<<20L, 'MB'),
            (1<<10L, 'kB'),
            (1, 'bytes')
        )
        if bytes == 1:
            return '1 byte'
        for factor, suffix in abbrevs:
            if bytes >= factor:
                break
        return '%.*f %s' % (precision, bytes / factor, suffix)