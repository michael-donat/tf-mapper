
import sys
import di, view, model.entity as entity, model.model as model
import server

from PyQt4 import QtCore, QtGui

from PyQt4 import QtGui, QtCore

if __name__ == '__main__':

    registry = model.Registry()
    navigator = model.Navigator()
    factory = model.RoomFactory()

    di.container.register('Config', model.Config())
    di.container.register('CoordinatesHelper', model.CoordinatesHelper())
    di.container.register('RoomFactory', factory)
    di.container.register('Registry', registry)
    di.container.register('Navigator', navigator)
    di.container.register('Map', model.Map)

    registry.roomShadow = view.RoomShadow()
    registry.roomShadow.hide()

    registry.shadowLink = view.ShadowLink()
    registry.shadowLink.hide()

    application = QtGui.QApplication(sys.argv)
    window = view.uiMainWindow()
    registry.mainWindow = window
    window.show()

    navigator = model.Navigator()

    window.mapView().scale(0.5,0.5)


    scene = factory.spawnLevel(0).getView()
    window.mapView().setScene(scene)

    """
    room = factory.createAt(QtCore.QPointF(0,0),scene)
    navigator.enableCreation(True)
    navigator.go(room, model.Direction.SE, model.Direction.NW)
    navigator.goWest()
    navigator.goUp()
    navigator.goDown()

    sceneB = factory.spawnLevel(1).getView()
    window.mapView().setScene(sceneB)
    room = factory.createAt(QtCore.QPointF(0,0),sceneB)
    navigator.go(room, model.Direction.S, model.Direction.N)
    """


    #window.mapView().setScene(scene)

    navigator.enableCreation(False)




    def zoomIn():
        window.mapView().scale(1.2, 1.2)

    def zoomOut():
        window.mapView().scale(0.8, 0.8)
        print window.mapView().transform()

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

    window.pushButton.clicked.connect(reportServerStatus)

    def dispatchServerCommand(command):
        if command == 'n': navigator.goNorth()
        if command == 'ne': navigator.goNorthEast()
        if command == 'e': navigator.goEast()
        if command == 'se': navigator.goSouthEast()
        if command == 's': navigator.goSouth()
        if command == 'sw': navigator.goSouthWest()
        if command == 'w': navigator.goWest()
        if command == 'nw': navigator.goNorthWest()
        if command == 'u': navigator.goUp()
        if command == 'd': navigator.goDown()

    registry.broadcasterServer = broadcasterServer = server.Broadcaster(23923)
    broadcasterServer.dataReceived.connect(dispatchServerCommand)

    sys.exit(application.exec_())


