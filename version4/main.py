
import sys
import di, view, model

from PyQt4 import QtCore, QtGui

from PyQt4 import QtGui, QtCore

if __name__ == '__main__':

    registry = model.Registry()
    navigator = model.Navigator()

    di.container.register('Config', model.Config())
    di.container.register('CoordinatesHelper', model.CoordinatesHelper())
    di.container.register('RoomFactory', model.RoomFactory())
    di.container.register('Registry', registry)
    di.container.register('Navigator', navigator)

    application = QtGui.QApplication(sys.argv)
    window = view.uiMainWindow()
    registry.mainWindow = window
    window.show()

    scene = view.uiMapLevel()
    #scene.setSceneRect(QtCore.QRectF(0,0,10,10))
    scene.setBackgroundBrush(QtGui.QColor(217, 217, 217))

    navigator = model.Navigator()

    window.mapView().setScene(scene)
    window.mapView().scale(0.5,0.5)

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

    window.zoomIn.clicked.connect(zoomIn)
    window.zoomOut.clicked.connect(zoomOut)
    window.walkerModeSelector.currentIndexChanged.connect(navigator.enableCreation)




    sys.exit(application.exec_())


