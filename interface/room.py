__author__ = 'thronag'

from PyQt4 import QtGui, QtCore

class Room(QtGui.QWidget):
    edgeSize=18
    def __init__(self, parent, x, y, exits):
        super(Room, self).__init__(parent)
        self.exits = exits
        self.x = x
        self.y = y
        self.initUI()
        print str.format("Creating room at x:{0}, y:{1}", x, y)
        self.activecolor = '#FF0000'
        self.idlecolor = '#000000'

        self.bordercolor = self.idlecolor

    def markActive(self):
        self.bordercolor = self.activecolor
        self.repaint()
        if hasattr(TFMapperRegistry.activeRoom, 'markInActive'):
            TFMapperRegistry.activeRoom.markInActive()
        TFMapperRegistry.activeRoom = self

    def markInActive(self):
        self.repaint()

    def mousePressEvent(self, QMouseEvent):
        self.markActive()

    def initUI(self):

        self.setGeometry(self.x, self.y, self.edgeSize, self.edgeSize)

    def paintEvent(self, e):
        #print 'PAINTING with'+self.bordercolor
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor(self.bordercolor)

        pen = QtGui.QPen(color)
        pen.setWidth(1)

        qp = QtGui.QPainter()

        sizeChunk = self.edgeSize / 6

        qp.begin(self)
        qp.setPen(pen)

        qp.drawRect(sizeChunk, sizeChunk, sizeChunk*4, sizeChunk*4)
        #qp.drawText(sizeChunk+10, sizeChunk+10, str.format("{0}x{1}", self.x, self.y))
        qp.end()

        qp.begin(self)
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor(self.idlecolor)
        pen.setColor(color)
        qp.setPen(pen)


        if 'n' in self.exits:
            qp.drawLine(sizeChunk*3, 0, sizeChunk*3, sizeChunk)
        if 'ne' in self.exits:
            qp.drawLine(sizeChunk*5, sizeChunk, sizeChunk*6, 0)
        if 'e' in self.exits:
            qp.drawLine(sizeChunk*5, sizeChunk*3, sizeChunk*6, sizeChunk*3)
        if 'se' in self.exits:
            qp.drawLine(sizeChunk*3, sizeChunk*3, sizeChunk*4, sizeChunk*4)
        if 's' in self.exits:
            qp.drawLine(sizeChunk*3, sizeChunk*5, sizeChunk*3, sizeChunk*6)
        if 'sw' in self.exits:
            qp.drawLine(0, sizeChunk*6, sizeChunk, sizeChunk*5)
        if 'w' in self.exits:
            qp.drawLine(0, sizeChunk*3, sizeChunk*1, sizeChunk*3)
        if 'nw' in self.exits:
            qp.drawLine(0, 0, sizeChunk, sizeChunk)
        qp.end()

        self.bordercolor = self.idlecolor