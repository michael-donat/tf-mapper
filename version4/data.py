__author__ = 'thornag'

import json, zlib
import base64
import textwrap, string
import os, shutil, sys
import model.model as model
import view
from PyQt4 import QtGui
import di
import sys

class Serializer:
    factory = di.ComponentRequest('RoomFactory')
    registry = di.ComponentRequest('Map')
    config = di.ComponentRequest('Config')
    coordinates=di.ComponentRequest('CoordinatesHelper')
    mapFile=None
    @staticmethod
    def saveMap(fileLocation, mapObject):

        zones = []
        zonesUnsorted = []

        for zone in mapObject.zones().itervalues():
            zonesUnsorted.append(zone)

        zonesSorted = sorted(zonesUnsorted, key=lambda zone: zone.id())

        for zone in zonesSorted:
            zones.append([str(zone.id()), str(zone.name())])

        zonesData = zones

        levels = []
        #print 'Gathering levels'
        levelsUnsorted = []
        for index, level in mapObject.levels().items():
            levelsUnsorted.append(level)

        levelsSorted = sorted(levelsUnsorted, key=lambda level: level.getMapIndex())

        for level in levelsSorted:
            levels.append([level.getId(), level.getMapIndex(), level.getView().sceneRect().x(),level.getView().sceneRect().y(), level.getView().sceneRect().width(), level.getView().sceneRect().height(), level.zone()])

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
        roomsData = sorted(rooms, key=lambda room: room[0])
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
        linksData = sorted(links, key=lambda link: link[0]+str(link[1])+link[4]+str(link[5]))
        #print 'Done -----'

        customLinks = []
        #print 'Gathering custom links'
        for link in customLinksSource:
            customLinks.append([link.getLeft()[0].getId(), link.getLeft()[1], link.getLeft()[2], link.getLeft()[3], link.getRight()[0].getId(), link.getRight()[1], link.getRight()[2], link.getRight()[3]])
        #print 'Serializing links'
        #linksData = base64.standard_b64encode(json.dumps(links))
        customLinksData = sorted(customLinks, key=lambda link: link[0]+str(link[1])+link[4]+str(link[5]))
        #print 'Done -----'

        labels = []
        for index, level in mapObject.levels().items():
            for item in level.getView().items():
                if isinstance(item, view.Label):
                    labels.append([item.x(), item.y(), level.getId(), str(item.toPlainText())])

        labels = sorted(labels, key=lambda label: label[0])

        #print 'Creating data dictionary'
        mapData = fileData = dict([('zones', zonesData),('levels', levelsData),('rooms', roomsData), ('links', linksData), ('customLinks', customLinksData), ('labels', labels)])

        #print 'Serializing it'
        fileData = json.dumps(fileData, indent=1)

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

        fileData = fileData

        #print 'Writing data dictionary'
        f = open(mapFile, 'wb')
        f.write(fileData)
        f.close()

        print 'Zones: %s' % len(mapData['zones'])
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
    def loadMap(window, mapView, QProgressBar, application):

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
            f = open(mapFile+'.txt', 'rb')
            decodeFile=False
        except IOError as e:
            f = open(mapFile, 'rb')
            decodeFile=True
        except: return False

        overall = (millis() - base)
        print 'File opened %s (%s) - %s' % (overall, millis() - base, mapFile)

        mapData = f.read()

        overall = (millis() - base)
        print 'File read %s (%s)' % (overall, millis() - overall)

        f.close()

        try:
            if not mapData[:1] == '{':
                mapData = zlib.decompress(mapData)
        except: pass

        overall = (millis() - base)
        print 'File decompressed read %s (%s)' % (overall, millis() - overall)

        try:
            if not mapData[:1] == '{':
                mapData = base64.standard_b64decode(mapData)
        except: pass

        try:
            mapData = json.loads(mapData)
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

        try:
            zonesRaw = mapData['zones']
        except: zonesRaw = []

        factory = Serializer.factory

        from PyQt4 import QtCore

        levelsById = {}

        zones = []

        window.selectZone.blockSignals(True)
        if len(zonesRaw) == 0: #its an old style map, lets adapt
            zone = factory.spawnZone('Untitled')
            zones.append(zone)
        else:
            for zoneTuple in zonesRaw:
                zone = factory.spawnZone(zoneTuple[1], zoneTuple[0])
                zones.append(zone)


        for zone in zones:
            window.selectZone.insertItem(0, zone.name(), str(zone.id()))

        window.selectZone.blockSignals(False)
        window.selectZone.setCurrentIndex(-1)
        window.selectZone.setCurrentIndex(0)
        Serializer.registry.setCurrentZone(window.selectZone.itemData(0).toString())

        mapModelRegistry = Serializer.registry

        for level in levels:
            try:
                level[6]
            except:
                level.append(str(zone.id()))

            levelModel = factory.spawnLevel(level[1], level[0], level[6])
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

        mapView.setScene(Serializer.registry.getZeroLevel().getView())

        aaa = Serializer.registry

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

class Importer():
    @staticmethod
    def importCmud(fileName=None):

        if fileName is False or fileName is None:
            fileName = QtGui.QFileDialog.getOpenFileName(None, 'Open CMUD map for import...', Serializer.getHomeDir(), 'Map (*.dbm)')
            if not fileName or fileName is None or str(fileName[0]) is "":
                return
            fileName = str(fileName)

        import sqlite3
        conn = sqlite3.connect(fileName)
        conn.text_factory = str

        cur = conn.cursor()
        cur.execute("PRAGMA encoding = \"UTF-8\";");
        cur.execute('SELECT * FROM ZoneTbl')

        rows = cur.fetchall()

        zoneMove={}

        zones=[]

        for row in rows:
            zones.append((row[0],row[1]))
            zoneMove[row[0]] = (row[21], row[22])

        zones.insert(0, zones[0][0])

        datalist = [('Zone', zones)]

        from formlayout import fedit

        result = fedit(datalist, title="Zone to import")

        if result is None:
            return

        zoneid = zones[result[0]+1][0]

        cur.execute('SELECT * FROM `ObjectTbl` where Z = 0 AND ZoneId = %d' % zoneid)

        rows = cur.fetchall()

        factory = Serializer.factory

        from PyQt4 import QtCore

        levels = Serializer.registry.levels()

        factor = 120 / Serializer.config.getSize() * 2

        importedRooms={}

        for row in rows:

            width = (row[9] - zoneMove[zoneid][0]) / factor
            height = (row[10] - zoneMove[zoneid][1])  / factor

            QPoint = QtCore.QPointF(width, height)

            room = factory.createAt(QPoint, levels[0].getView(), row[0])

            importedRooms[row[0]] = room

        """def linkRooms(self, leftRoom, leftExit, rightRoom, rightExit, QGraphicsScene=None, leftLinkCustomLabel=None, rightLinkCustomLabel=None, leftLinkRebind=None, rightLinkRebind=None):"""

        cur.execute('SELECT * FROM `ExitTbl`')

        rows = cur.fetchall()

        directories = {
            1: model.Direction.N,
            2: model.Direction.NE,
            3: model.Direction.E,
            4: model.Direction.SE,
            5: model.Direction.S,
            6: model.Direction.SW,
            7: model.Direction.W,
            8: model.Direction.NW,
            9: model.Direction.U,
            10: model.Direction.D
        }

        alreadyLinked=[]

        for row in rows:

            if row[0] in alreadyLinked or row[1] in alreadyLinked: continue

            leftRoom = row[2]
            rightRoom = row[3]
            leftExit = row[19]+1
            rightExit = row[20]+1

            alreadyLinked.append(row[0])
            alreadyLinked.append(row[1])

            if leftExit not in range(1,10) or rightExit not in range(1,10): continue

            if leftRoom not in importedRooms or rightRoom not in importedRooms: continue

            leftRoom = importedRooms[leftRoom]
            rightRoom = importedRooms[rightRoom]

            leftExit = directories[leftExit]
            rightExit = directories[rightExit]

            try:
                leftRoom.addExit(leftExit)
                rightRoom.addExit(rightExit)

                factory.linkRooms(leftRoom, leftExit, rightRoom, rightExit, levels[0].getView())
            except: pass

