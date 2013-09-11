
import sys, getopt
import di, view, model.entity as entity, model.model as model, model.ui as modelui
import network
from data import Serializer
from data import Importer
import re
from options import getOptions
from callbacks import *
from pathfinder import highlightPath

from PyQt4 import QtCore, QtGui

if __name__ == '__main__':

    application = QtGui.QApplication(sys.argv)
    application.setStyle('plastique')

    QPixmap = QtGui.QPixmap("ui/icons/hychsohn_256x256x32_transparent.png")
    QSplashScreen = QtGui.QSplashScreen(QPixmap)
    QSplashScreen.show()

    QProgressBar = QtGui.QProgressBar(QSplashScreen)
    QProgressBar.setMinimum(0)
    QProgressBar.setMaximum(100)
    QProgressBar.setTextVisible(False)
    QProgressBar.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
    QProgressBar.setFixedWidth(250)
    QProgressBar.move(0, 220)

    QProgressBar.show()

    QSplashScreen.raise_()

    application.processEvents()

    options = getOptions()

    Serializer.mapFile = options.mapFile

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

    window = view.uiMainWindow()
    QProgressBar.setValue(20)
    application.processEvents()
    if options.noPanels: window.hidePanels()

    registry.mainWindow = window

    import os

    baseDir = os.getenv("USERPROFILE") if sys.platform == 'win32' else os.getenv("HOME")
    baseDir = baseDir+'/.tf-mapper/'

    sys.path.insert(0, baseDir)

    import shortcuts
    import roomClasses

    window.buildShortcuts(shortcuts)
    window.buildClasses(roomClasses)

    sys.path.pop(0)

    #adding panel actions
    toolsPanelAction = window.uiComponentToolsPanel.toggleViewAction()
    toolsPanelAction.setShortcut('CTRL+T')
    window.menuView.addAction(toolsPanelAction)
    propsPanelAction = window.uiComponentPropertiesPanel.toggleViewAction()
    propsPanelAction.setShortcut('CTRL+P')
    window.menuView.addAction(propsPanelAction)

    if options.width and options.height: window.resize(int(options.width), int(options.height))

    window.compassU.setShortcut(QtGui.QApplication.translate("MainWindow", options.keyUp, None, QtGui.QApplication.UnicodeUTF8))
    window.compassD.setShortcut(QtGui.QApplication.translate("MainWindow", options.keyDown, None, QtGui.QApplication.UnicodeUTF8))


    roomProperties = modelui.RoomProperties(window)
    #navigator.roomSelectedSignal.connect(roomProperties.updatePropertiesFromRoom)

    di.container.register('Properties', roomProperties)

    navigator = model.Navigator()

    window.mapView().scale(0.5,0.5)
    QProgressBar.setValue(35)
    application.processEvents()

    QProgressBar.setValue(70)
    application.processEvents()
    def zoomIn():
        window.mapView().scale(1.2, 1.2)

    def zoomOut():
        window.mapView().scale(0.8, 0.8)
        #print window.mapView().transform()

    registry.zoonInFunction = zoomIn
    registry.zoonOutFunction = zoomOut

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
    window.sameUpDown.toggled.connect(navigator.enableSameUpDown)

    def reportSceneRect():
        print window.mapView().sceneRect()

    def reportActiveRoom():
        print registry.currentlyVisitedRoom.getId()

    def reportServerStatus():
        print registry.broadcasterServer.tcpServer().isListening()

    def dumpRoom():
        room = registry.currentlyVisitedRoom
        print registry.currentlyVisitedRoom


    def fireCommand():
        dispatchServerCommand(str(window.commandInput.text()))

    window.commandTrigger.clicked.connect(fireCommand)
    QProgressBar.setValue(80)
    application.processEvents()

    def commandDeleteActiveRoom():
        if registry.currentlyVisitedRoom is not None:
            commandDeleteRoomById(registry.currentlyVisitedRoom.getId())

    def commandDeleteRoomById(roomId):
        roomToDelete = mapModel.getRoomById(roomId)
        if roomToDelete is not None:
            roomToDelete.delete()

    def dispatchServerCommand(command):
        if command == 'navigate:exit:n': navigator.goNorth()
        if command == 'navigate:exit:polnoc': navigator.goNorth()
        if command == 'navigate:exit:ne': navigator.goNorthEast()
        if command == 'navigate:exit:polnocny-wschod': navigator.goNorthEast()
        if command == 'navigate:exit:e': navigator.goEast()
        if command == 'navigate:exit:wschod': navigator.goEast()
        if command == 'navigate:exit:se': navigator.goSouthEast()
        if command == 'navigate:exit:poludniowy-wschod': navigator.goSouthEast()
        if command == 'navigate:exit:s': navigator.goSouth()
        if command == 'navigate:exit:poludnie': navigator.goSouth()
        if command == 'navigate:exit:sw': navigator.goSouthWest()
        if command == 'navigate:exit:poludniowy-zachod': navigator.goSouthWest()
        if command == 'navigate:exit:w': navigator.goWest()
        if command == 'navigate:exit:zachod': navigator.goWest()
        if command == 'navigate:exit:nw': navigator.goNorthWest()
        if command == 'navigate:exit:polnocny-zachod': navigator.goNorthWest()
        if command == 'navigate:exit:u': navigator.goUp()
        if command == 'navigate:exit:gora': navigator.goUp()
        if command == 'navigate:exit:d': navigator.goDown()
        if command == 'navigate:exit:dol': navigator.goDown()
        if command == 'revert': revertToLastRoom()

        if command == 'map:undo': navigator.undoCreation()
        if command == 'map:revert': revertToLastRoom()

        if command == 'map:mode:walk': window.walkerModeSelector.setCurrentIndex(int(0))
        if command == 'map:mode:create': window.walkerModeSelector.setCurrentIndex(int(1))
        if command == 'map:mode:toggle': window.walkerModeSelector.setCurrentIndex(int(not window.walkerModeSelector.currentIndex()))

        if command == 'map:zoom:in': zoomIn()
        if command == 'map:zoom:out': zoomOut()

        if command == 'map:room:delete': commandDeleteActiveRoom()

        if command == 'path:clear': highlightPath(mapModel, registry.currentlyVisitedRoom, None)

        match =  re.match(r'map:room:delete:(.*)', command)
        if match is not None:
            commandDeleteRoomById(match.group(1))

        match =  re.match(r'path:highlight:(.*)', command)
        if match is not None:
            highlightPath(mapModel, registry.currentlyVisitedRoom, str(match.group(1)))


        match =  re.match(r'navigate:custom:(.*)', command)
        if match is not None:
            navigator.goCustom(match.group(1))

        match =  re.match(r'navigate:follow:(.*)', command)
        if match is not None:
            navigator.goFollow(match.group(1))

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

        rightRebind = leftRebind = rightLinkMask = leftLinkMask = None

        if model.Direction.OTHER in [leftExit, rightExit]:
            leftRebind = window.manualLinkCustomLinkLeft.text() if len(window.manualLinkCustomLinkLeft.text()) else None
            rightRebind = window.manualLinkCustomLinkRight.text() if len(window.manualLinkCustomLinkRight.text()) else None

        factory.linkRooms(\
            leftRoom, leftExit, rightRoom, rightExit, \
            rightRoom.getLevel().getView() if leftExit not in [model.Direction.U, model.Direction.D] and rightExit not in [model.Direction.U, model.Direction.D] and rightRoom.getLevel().getId() == leftRoom.getLevel().getId() else None,\
            None, \
            None, \
            leftRebind, \
            rightRebind
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

    def switchClassesShowing(show):
        registry.applyClasses = show

    def switchColorsShowing(show):
        registry.applyColors = show

    registry.blockCreation = False

    def switchCreationBlock(show):
        registry.blockCreation = not show


    def renameCurrentZone():
        currentZone = mapModel.currentZone()
        zoneName = QtGui.QInputDialog.getText(window, 'Rename zone', 'Name', QtGui.QLineEdit.Normal, currentZone.name())
        zoneName, ok = zoneName

        if not ok:
            return

        currentZone.setName(zoneName)
        window.selectZone.setItemText(window.selectZone.currentIndex(), zoneName)


    window.menuActionShowClasses.toggled.connect(switchClassesShowing)
    window.menuActionShowColors.toggled.connect(switchColorsShowing)
    #window.actionEnableCreation.toggled.connect(switchCreationBlock)
    window.actionRenameZone.triggered.connect(renameCurrentZone)


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

    def processZoneSelect(zoneindex):
        if zoneindex == -1: return
        zoneId = window.selectZone.itemData(zoneindex).toString()
        navigator.changeZone(zoneId)
        navigator.switchLevel(0)

    window.selectZone.currentIndexChanged.connect(processZoneSelect)

    window.uiCreationClass.currentIndexChanged.connect(applyCreationClass)
    window.uiCreationClassApply.clicked.connect(reapplyCreationClass)

    window.centerOnMove.toggled.connect(registry.setCenterAt)
    QProgressBar.setValue(90)
    application.processEvents()

    if not options.noServer:
        if not options.spawnRemoteConnection:
            registry.connection = broadcasterServer = network.Broadcaster(23923)
            broadcasterServer.dataReceived.connect(dispatchServerCommand)
        else:
            registry.connection = clientServer = network.Listener('localhost', 9999)
            clientServer.dataReceived.connect(dispatchServerCommand)


    from formlayout import fedit

    settings = QtCore.QSettings('MudMapper', 'net.michaeldonat')

    def showPreferences():
        width = settings.value('width', 400).toInt()[0]
        height = settings.value('height', 200).toInt()[0]
        server = settings.value('server', False).toBool()
        panels = settings.value('panels', False).toBool()
        room = str(settings.value('room', '').toString())
        map = str(settings.value('map', '').toString())

        datalist = [('Width', width), ('Height', height), ('Disable socket server', server),('Show panels', panels),('Start room', room), ('Map file', map)]

        result = fedit(datalist, title="Preferences")

        if result is not None:
            settings.setValue('width', result[0])
            settings.setValue('height', result[1])
            settings.setValue('server', result[2])
            settings.setValue('panels', result[3])
            settings.setValue('room', result[4])
            settings.setValue('map', result[5])

    window.actionPreferences.triggered.connect(showPreferences)


    def openMap(fileName=None):

        if not fileName or fileName is None:
            fileName = QtGui.QFileDialog.getOpenFileName(None, 'Open map...', Serializer.getHomeDir(), 'Map (*.map *.db)')
            if not fileName or fileName is None or str(fileName[0]) is "":
                    return

        QProgressBar = QtGui.QProgressDialog(window)
        QProgressBar.setMinimum(0)
        QProgressBar.setMaximum(100)
        QProgressBar.setLabelText('Loading %s' % fileName)
        QProgressBar.setFixedWidth(250)

        QProgressBar.show()

        clearMap()
        Serializer.mapFile = fileName
        result = Serializer.loadMap(window, window.mapView(), QProgressBar, application)
        updateTitle()
        QProgressBar.setValue(100)
        QProgressBar.hide()
        QProgressBar.destroy()
        QProgressBar = None
        return result

    def clearMap():
        Serializer.mapFile = None
        mapModel.clear()
        registry.reinit()
        updateTitle()
        window.selectZone.clear()

    def dumpMap():
        if Serializer.mapFile is None:
            fileName = QtGui.QFileDialog.getSaveFileNameAndFilter(None, 'Save map...', Serializer.getHomeDir(), 'Map (*.map *.db)')

            if str(fileName[0]) is "":
                return
            Serializer.mapFile = str(fileName[0])
        Serializer.saveMap('123', mapModel)

    def dumpNewMap():
        Serializer.mapFile = None
        dumpMap()

    def newMap():
        clearMap()
        createNewZone('Zone 1')

    window.menuActionOpen.triggered.connect(openMap)
    window.menuActionNew.triggered.connect(newMap)
    window.menuActionSave.triggered.connect(dumpMap)
    window.menuActionSaveAs.triggered.connect(dumpNewMap)


    def updateTitle():
        if Serializer.mapFile is not None:
            window.setWindowTitle('MudMapper by thornag - %s' % Serializer.mapFile)
        else:
            window.setWindowTitle('MudMapper by thornag')

    updateTitle()


    #exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
    #exitAction.setShortcut('Ctrl+Q')
    #exitAction.setStatusTip('Exit application')
    #exitAction.triggered.connect(QtGui.qApp.quit)

    def createNewZone(name=None):
        if name is None:
            zoneName = QtGui.QInputDialog.getText(window, 'New zone', 'Name', QtGui.QLineEdit.Normal, '')
            zoneName, ok = zoneName

            if not ok:
                return

        else:
            zoneName = name

        zone = factory.spawnZone(zoneName)
        window.selectZone.addItem(zone.name(), str(zone.id()))

        window.selectZone.setCurrentIndex(window.selectZone.count()-1)

        scene = factory.spawnLevel(0).getView()
        window.mapView().setScene(scene)



    window.addZoneButton.clicked.connect(createNewZone)

    window.show()
    window.raise_()

    QProgressBar.setValue(100)
    application.processEvents()
    QSplashScreen.finish(window)
    application.processEvents()
    createLevel = True


    if Serializer.mapFile is not None:
        resop = openMap(Serializer.mapFile)
        if resop is not False and resop is not None:
            createLevel = False
            if options.room: lookupRoom(options.room)
    application.processEvents()

    if createLevel:
        zone = createNewZone('Zone 1')
        navigator.enableCreation(False)
    application.processEvents()

    window.actionImportCMUD.triggered.connect(Importer.importCmud)

    sys.exit(application.exec_())




