__author__ = 'thornag'

import model
from PyQt4 import QtGui

class Factory:
    def getRoomView(self, modelRoom):
        if isinstance(model.modelRoom):
            raise Exception('Factory::getRoomItem expects the 1st parameter to be model.Room')

        viewRoom = QtGui.QGraphicsItem(modelRoom) #obioysly specialised as our room
        modelRoom.setView(viewRoom)

        return viewRoom

    def signalSelection(self):
        #when selected it will emit signal that it has been selected


class Room(QtGui.QGraphicsItem):
    def __init__(self):
        super(Room, self).__init__(self)

    def selectHandler