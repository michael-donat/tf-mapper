
from PyQt4 import QtCore, QtGui

import model


class Room(QtGui.QGraphicsItem):
    BoundingRect = QtCore.QRectF(0,0,30,30)
    roomModel=None
    def __init__(self, roomModel):

        super(Room, self).__init__()
        self.color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
                                  QtCore.qrand() % 256)

        self.roomModel = roomModel
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable)

    def boundingRect(self):
        return Room.BoundingRect


    def paint(self, painter, option, widget):

        if self.isSelected():
            painter.setPen(QtCore.Qt.DashLine)
            painter.drawRect(0,0,30,30)

        else:
            painter.setPen(QtCore.Qt.SolidLine)

        if self.roomModel.isVisited():
            painter.setBrush(QtGui.QColor(255,255,255))
        else:
            painter.setBrush(self.color)

        painter.drawRect(5, 5, 20, 20)

        if (self.roomModel.hasExit(model.Direction.N)):
            painter.drawLine(15, 0, 15, 5)

        if (self.roomModel.hasExit(model.Direction.NE)):
            painter.drawLine(25, 5, 30, 0)

        if (self.roomModel.hasExit(model.Direction.E)):
            painter.drawLine(25, 15, 30, 15)

        if (self.roomModel.hasExit(model.Direction.SE)):
            painter.drawLine(25, 25, 30, 30)

        if (self.roomModel.hasExit(model.Direction.S)):
            painter.drawLine(15, 25, 15, 30)

        if (self.roomModel.hasExit(model.Direction.SW)):
            painter.drawLine(0, 30, 5, 25)

        if (self.roomModel.hasExit(model.Direction.W)):
            painter.drawLine(0, 15, 5, 15)

        if (self.roomModel.hasExit(model.Direction.NW)):
            painter.drawLine(0, 0, 5, 5)

        print 'PRINTED'

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        print QGraphicsSceneMouseEvent.modifiers() & QtCore.Qt.ShiftModifier
        if not QGraphicsSceneMouseEvent.modifiers() & QtCore.Qt.ShiftModifier:
            for item in self.scene().selectedItems():
                item.setSelected(False)

        self.setSelected(True)


class MapView(QtGui.QGraphicsView):
    def __init__(self):
        super(MapView, self).__init__()

    def contextMenuEvent(self, event):
        eventPos = event.pos()
        print self.scene().sceneRect()
        menu = QtGui.QMenu()
        action = QtGui.QAction(str.format('Add room at {0}x{1}', eventPos.x(), eventPos.y()), self)
        action.triggered.connect(lambda: self.createRoomAt(QtCore.QPoint(eventPos.x()-15, eventPos.y()-15)))
        menu.addAction(action)
        menu.exec_(event.globalPos())
        event.accept()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Up:
            for item in self.scene().selectedItems():
                item.moveBy(0,-1)

        if QKeyEvent.key() == QtCore.Qt.Key_Down:
            for item in self.scene().selectedItems():
                item.moveBy(0,1)

        if QKeyEvent.key() == QtCore.Qt.Key_Left:
            for item in self.scene().selectedItems():
                item.moveBy(-1,0)

        if QKeyEvent.key() == QtCore.Qt.Key_Right:
            for item in self.scene().selectedItems():
                item.moveBy(1,0)

        super(MapView, self).keyPressEvent(QKeyEvent)

    def createRoomAt(self, pos):

        room = Room(model.Room(model.Direction.W))

        self.scene().addItem(room)
        self.scene().addRect(0,0,10,10)
        room.setPos(pos.x(), pos.y())
        room.show()

