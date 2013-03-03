
import sys
from PyQt4 import QtGui, QtCore
import view
import model

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.storage

    scene = QtGui.QGraphicsScene()

    room = view.Room(model.Room(model.Direction.N | model.Direction.NE | model.Direction.E | model.Direction.SE | model.Direction.S | model.Direction.SW | model.Direction.W | model.Direction.NW))

    scene.addItem(room)

    room = view.Room(model.Room(model.Direction.NW))

    scene.addItem(room)

    scene.setSceneRect(QtCore.QRectF(0,0,100,100))

    scene.setBackgroundBrush(QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
                                          QtCore.qrand() % 256))

    room.moveBy(30,30)

    room = view.Room(model.Room(model.Direction.W))

    scene.addItem(room)

    room.moveBy(30,0)
    room.roomModel.setVisited(True)

    view = view.MapView()


    view.setScene(scene)
    view.setSceneRect(QtCore.QRectF(0,0,500,500))
    view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    view.show()


    sys.exit(app.exec_())