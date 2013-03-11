
import sys, getopt
import di, view, model.entity as entity, model.model as model, model.ui as modelui
import network
from data import Serializer
import re

from PyQt4 import QtCore, QtGui

from PyQt4 import QtGui, QtCore

if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], "rm:", ["map=", "remote", "disable-connectivity", "no-panels"])

    spawnRemoteConnection = False
    noServer = False
    mapFile='map.db'
    noPanels=False

    for opt, arg in opts:
        if opt in ("-m", "--map"):
            mapFile=arg
        if opt in ("-r", "--remote"):
            spawnRemoteConnection = True
        if opt == "--disable-connectivity":
            noServer = True
        if opt == "--no-panels":
            noPanels = True

    Serializer.mapFile = mapFile

    registry = model.Registry()
    navigator = model.Navigator()
    factory = model.RoomFactory()
    mapModel = model.Map()
    clipboard = model.Clipboard()

    di.container.register('Config', model.Config())
    di.container.register('CoordinatesHelper', model.CoordinatesHelper())
    di.container.register('RoomFactory', factory)
    di.container.register('Registry', registry)
    di.container.register('Navigator', navigator)
    di.container.register('Map', mapModel)
    di.container.register('Clipboard', clipboard)

    registry.roomShadow = view.RoomShadow()
    registry.roomShadow.hide()

    registry.shadowLink = view.ShadowLink()
    registry.shadowLink.hide()

    application = QtGui.QApplication(sys.argv)
    application.setStyle('plastique')
    window = view.uiMainWindow()
    if noPanels: window.hidePanels()
    import roomClasses
    window.buildClasses(roomClasses)
    registry.mainWindow = window

    window.show()

    roomProperties = modelui.RoomProperties(window)
    #navigator.roomSelectedSignal.connect(roomProperties.updatePropertiesFromRoom)

    di.container.register('Properties', roomProperties)

    navigator = model.Navigator()

    window.mapView().scale(0.5,0.5)

    if not Serializer.loadMap(window.mapView()):
        scene = factory.spawnLevel(0).getView()
        window.mapView().setScene(scene)
        navigator.enableCreation(False)

    def zoomIn():
        window.mapView().scale(1.2, 1.2)

    def zoomOut():
        window.mapView().scale(0.8, 0.8)
        #print window.mapView().transform()

    def deb(str):
        print str

    window.compassN.clicked.connect(navigator.goNorth)
    window.compassNE.clicked.connect(navigator.goNorthEast)
    window.compassE.clicked.connect(navigator.goEast)
    window.compassSE.clicked.connect(navigator.goSouthEast)
    window.compassS.clicked.connect(navigator.goSouth)
    window.compassSW.clicked.connect(navigator.goSouthWest)
    window.compassW.clicked.connect(navigator.goWest)
    window.compassNW.clicked.connect(navigator.goNorthWest)
    window.compassU.clicked.connect(navigator.goUp)
    window.compassD.clicked.connect(navigator.goDown)

    window.zoomIn.clicked.connect(zoomIn)
    window.zoomOut.clicked.connect(zoomOut)
    window.goLevelUp.clicked.connect(navigator.goLevelUp)
    window.goLevelDown.clicked.connect(navigator.goLevelDown)
    window.walkerModeSelector.currentIndexChanged.connect(navigator.enableCreation)
    window.autoPlacement.toggled.connect(navigator.enableAutoPlacement)

    def reportSceneRect():
        print window.mapView().sceneRect()

    def reportActiveRoom():
        print registry.currentlyVisitedRoom.getId()

    def reportServerStatus():
        print registry.broadcasterServer.tcpServer().isListening()

    def dumpMap():
        Serializer.saveMap('123', mapModel)

    def dumpRoom():
        room = registry.currentlyVisitedRoom
        print registry.currentlyVisitedRoom

    window.debugButton.clicked.connect(dumpRoom)

    window.pushButton.clicked.connect(dumpMap)

    def fireCommand():
        dispatchServerCommand(str(window.commandInput.text()))

    window.commandTrigger.clicked.connect(fireCommand)

    def dispatchServerCommand(command):
        print 'received command %s' % command
        if command == 'navigate:n': navigator.goNorth()
        if command == 'navigate:polnoc': navigator.goNorth()
        if command == 'navigate:ne': navigator.goNorthEast()
        if command == 'navigate:polnocny-wschod': navigator.goNorthEast()
        if command == 'navigate:e': navigator.goEast()
        if command == 'navigate:wschod': navigator.goEast()
        if command == 'navigate:se': navigator.goSouthEast()
        if command == 'navigate:poludniowy-wschod': navigator.goSouthEast()
        if command == 'navigate:s': navigator.goSouth()
        if command == 'navigate:poludnie': navigator.goSouth()
        if command == 'navigate:sw': navigator.goSouthWest()
        if command == 'navigate:poludniowy-zachod': navigator.goSouthWest()
        if command == 'navigate:w': navigator.goWest()
        if command == 'navigate:zachod': navigator.goWest()
        if command == 'navigate:nw': navigator.goNorthWest()
        if command == 'navigate:polnocny-zachod': navigator.goNorthWest()
        if command == 'navigate:u': navigator.goUp()
        if command == 'navigate:gora': navigator.goUp()
        if command == 'navigate:d': navigator.goDown()
        if command == 'navigate:dol': navigator.goDown()
        if command == 'revert': revertToLastRoom()

        match =  re.match(r'navigate:custom:(.*)', command)
        if match is not None:
            navigator.goCustom(match.group(1))

        match =  re.match(r'lookup:([a-z0-9\-]*)', command)
        if match is not None:
            lookupRoom(match.group(1))

    def executeManualLink():
        leftRoomId = str(window.manualLinkRoomLeft.text())
        rightRoomId = str(window.manualLinkRoomRight.text())
        leftExit = window.manualLinkLinkLeft.currentText()
        rightExit = window.manualLinkLinkRight.currentText()

        if not leftRoomId or not rightRoomId or not leftExit or not rightExit: return False

        leftRoom = mapModel.rooms()[leftRoomId] if leftRoomId in mapModel.rooms() else None
        rightRoom = mapModel.rooms()[rightRoomId] if rightRoomId in mapModel.rooms() else None

        if not leftRoom or not rightRoom: return False

        leftExit = model.Direction.mapFromLabel(leftExit)
        rightExit = model.Direction.mapFromLabel(rightExit)

        rightLinkMask = leftLinkMask = None

        if model.Direction.OTHER in [leftExit, rightExit]:
            leftLinkMask = window.manualLinkCustomLinkLeft.text()
            rightLinkMask = window.manualLinkCustomLinkRight.text()

        factory.linkRooms(\
            leftRoom, leftExit, rightRoom, rightExit, \
            rightRoom.getLevel().getView() if leftExit not in [model.Direction.U, model.Direction.D] and rightExit not in [model.Direction.U, model.Direction.D] and rightRoom.getLevel().getId() == leftRoom.getLevel().getId() else None,\
            leftLinkMask, \
            rightLinkMask \
        )

        leftRoom.addExit(leftExit)
        rightRoom.addExit(rightExit)
        leftRoom.getView().update()
        rightRoom.getView().update()

    def copyManualLinkRoomId(isRight=False):
        if not isRight:
            window.manualLinkRoomLeft.setText(window.roomIdDisplay.text())
        else:
            window.manualLinkRoomRight.setText(window.roomIdDisplay.text())

    def manualMergeRooms():
        leftRoomId = str(window.manualLinkRoomLeft.text())
        rightRoomId = str(window.manualLinkRoomRight.text())

        if not leftRoomId or not rightRoomId: return False

        leftRoom = mapModel.rooms()[leftRoomId] if leftRoomId in mapModel.rooms() else None
        rightRoom = mapModel.rooms()[rightRoomId] if rightRoomId in mapModel.rooms() else None

        if not leftRoom or not rightRoom: return False

        navigator.mergeRooms(rightRoom, leftRoom)

    def manualLinkInsertFromSelection():
        items = registry.currentLevel.getView().selectedItems()
        try:
            window.manualLinkRoomLeft.setText(items[0].getModel().getId())
            window.manualLinkRoomRight.setText(items[1].getModel().getId())
        except: return False

    def manualLookupRoom():
        if not window.roomIdDisplay.text(): return False
        lookupRoom(str(window.roomIdDisplay.text()))

    def lookupRoom(roomId):
        roomId = str(roomId)
        if roomId not in mapModel.rooms().keys(): return False
        room = mapModel.rooms()[roomId]
        navigator.markVisitedRoom(room)

    def revertToLastRoom():
        if registry.previouslyVisitedRoom is not None:
            lookupRoom(registry.previouslyVisitedRoom.getId())

    def toggleCustomLinkInput(isRight=False):
        if isRight:
            if window.manualLinkLinkRight.currentText() == 'Custom':
                window.manualLinkCustomLinkRight.setEnabled(True)
            else:
                window.manualLinkCustomLinkRight.setEnabled(False)
        else:
            if window.manualLinkLinkLeft.currentText() == 'Custom':
                window.manualLinkCustomLinkLeft.setEnabled(True)
            else:
                window.manualLinkCustomLinkLeft.setEnabled(False)


    window.manualLinkRoomLeftInsert.clicked.connect(lambda: copyManualLinkRoomId())
    window.manualLinkRoomRightInsert.clicked.connect(lambda: copyManualLinkRoomId(True))

    window.manualLinkExecute.clicked.connect(executeManualLink)
    window.manualMergeExecute.clicked.connect(manualMergeRooms)
    window.manualLinkInsertFromSelection.clicked.connect(manualLinkInsertFromSelection)
    window.manualLookupRoom.clicked.connect(manualLookupRoom)
    window.manualLinkLinkLeft.currentIndexChanged.connect(lambda: toggleCustomLinkInput())
    window.manualLinkLinkRight.currentIndexChanged.connect(lambda: toggleCustomLinkInput(True))


    def showCreationColorPicker():
        if registry.defColor:
            color = QtGui.QColorDialog.getColor(QtGui.QColor(registry.defColor))
        else: color = QtGui.QColorDialog.getColor()

        if not color.isValid(): return
        registry.setDefaultColor(color)
        window.uiCreationColor.blockSignals(True)
        window.uiCreationColor.setText(registry.defColor)
        window.uiCreationColor.blockSignals(False)
        window.uiCreationColor.textChanged.emit(registry.defColor)

    def updateSelectionColor(color):
        for item in window.mapView().scene().selectedItems():
            item.getModel().setProperty(model.Room.PROP_COLOR, str(color))

    window.uiCreationColor.textChanged.connect(registry.setDefaultColor)
    window.uiCreationColor.textChanged.connect(updateSelectionColor)
    window.uiCreationColorPicker.clicked.connect(showCreationColorPicker)

    def reapplyCreationClass():
        window.uiCreationClass.currentIndexChanged.emit(window.uiCreationClass.currentIndex())

    def applyCreationClass(roomClassIndex):
        registry.setDefaultClass(window.uiCreationClass.currentText())
        for item in window.mapView().scene().selectedItems():
            item.getModel().setProperty(model.Room.PROP_CLASS, window.uiCreationClass.currentText())
            pass


    window.uiCreationClass.currentIndexChanged.connect(applyCreationClass)
    window.uiCreationClassApply.clicked.connect(reapplyCreationClass)

    window.centerOnMove.toggled.connect(registry.setCenterAt)

    if not noServer:
        if not spawnRemoteConnection:
            registry.connection = broadcasterServer = network.Broadcaster(23923)
            broadcasterServer.dataReceived.connect(dispatchServerCommand)
        else:
            registry.connection = clientServer = network.Listener('localhost', 9999)
            clientServer.dataReceived.connect(dispatchServerCommand)

    sys.exit(application.exec_())


