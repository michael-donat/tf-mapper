__author__ = 'thornag'

from PyQt4 import QtGui, QtCore

class Map(QtCore.QObject):
    def __init__(self):
        super(Map, self).__init__()

    def getMiddlePoint(self):
        return self.middlePoint

    def draw(self, parent, size):
        self.middlePoint = size/2
        self.widget= QtGui.QWidget(parent)
        self.widget.setStyleSheet("background-color: #E8E8E8")
        self.widget.setGeometry(0, 0, size, size)
        self.widget.installEventFilter(self)
        self.widget.show()

    def updateGeometry(self, x=None, y=None):

        print 'updateGeometry called with x:'+str(x)+' y:'+str(y)

        x = self.widget.width() / 2 if x is None else x
        y = self.widget.height() / 2 if y is None else y

        self.lastRequestedGeometry = (x, y)

        parent = self.widget.parentWidget()

        hookPointX = x - (parent.width()/2)
        hookPointY = y - (parent.height()/2)

        print 'updateGeometry has parent size of x:'+str(parent.width())+' y:'+str(parent.height())
        print 'updateGeometry is setting hook points x:'+str(hookPointX)+' y:'+str(hookPointY)

        self.widget.move(-1 * hookPointX, -1 * hookPointY)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.updateGeometry(event.x(), event.y())

        if event.type() == QtCore.QEvent.Paint:
            self.updateGeometry(self.lastRequestedGeometry[0], self.lastRequestedGeometry[1])

        return False



class Level:
    """
    Represents a widget within the display frame that acts as a
    map level, every map room should belong to a map level
    """

class Room:
    """
    Represents a room on a map, has it's own coordinates relative to
    area level (canvas/widget at which map is drawn)
    """
    def __init__(self):
        pass


class Exit:
    """
    Represents a room on a map, has it's own coordinates relative to
    area level (canvas/widget at which map is drawn)
    """
    def __init__(self):
        pass

class Link:
    """
    Represents a link betwee two exists, every exit should have a link if it(exit) is connected
     to another room's exit
    """
    def __init__(self):
        pass