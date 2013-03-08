
from PyQt4 import QtGui, QtCore
import entity
import model

class PropertiesExitsTableModel(QtCore.QAbstractTableModel):
    __room=None
    def __init__(self, roomModel):
        super(PropertiesExitsTableModel, self).__init__()
        self.__room = roomModel



    def rowCount(self, QModelIndex):
        items = set(self.__room.getLinks().values()+self.__room.getCustomLinks())
        return len(items)
    def columnCount(self, QModelIndex):
        #1-exit, 2-label, 3-destination
        return 3
    def data(self, QModelIndex, role):
        if role == QtCore.Qt.DisplayRole:
            items = set(self.__room.getLinks().values()+self.__room.getCustomLinks())
            items = list(items)
            link = items[QModelIndex.row()]
            sourceSide = link.getSourceSideFor(self.__room)
            if QModelIndex.column() == 0:
                return model.Direction.mapToLabel(sourceSide[1])
            if QModelIndex.column() == 1:
                return sourceSide[2]
            if QModelIndex.column() == 2:
                return link.getDestinationFor(self.__room).getId()



class RoomProperties(QtCore.QObject):
    __uiRoomId=None
    __uiRoomName=None
    __uiCommands=None
    __uiColor=None
    __room=None
    __uiExitsTable=None
    def __init__(self, mainWindow):
        super(RoomProperties, self).__init__()
        self.__uiRoomId = mainWindow.uiPropertiesRoomId
        self.__uiRoomName = mainWindow.uiPropertiesRoomName
        self.__uiCommands = mainWindow.uiPropertiesCommands
        self.__uiColor = mainWindow.uiPropertiesColor
        self.__uiExitsTable = mainWindow.uiPropertiesExits

        mainWindow.uiPropertiesColorPicker.clicked.connect(self.pickColor)

        self.__uiRoomName.textEdited.connect(self.updateRoomFromProperties)
        self.__uiCommands.textChanged.connect(self.updateRoomFromProperties)
        self.__uiColor.textEdited.connect(self.updateRoomFromProperties)

    def pickColor(self):
        QColor = QtGui.QColorDialog.getColor()
        self.__uiColor.setText(QColor.name())
        self.__uiColor.textEdited.emit('dummy')

    def updatePropertiesFromRoom(self, roomModel):
        self.__uiRoomId.setText(roomModel.getId())
        self.__uiRoomName.setText(roomModel.getProperty('name'))
        self.__uiCommands.blockSignals(True)
        self.__uiCommands.setPlainText(roomModel.getProperty('commands'))
        self.__uiCommands.blockSignals(False)
        self.__uiColor.setText(str(roomModel.getProperty('color')))
        self.__room = roomModel

        model = PropertiesExitsTableModel(roomModel)
        self.__uiExitsTable.setModel(model)


    def updateRoomFromProperties(self):
        self.__room.setProperty(entity.Room.PROP_NAME, self.__uiRoomName.text())
        self.__room.setProperty(entity.Room.PROP_COMMANDS, self.__uiCommands.toPlainText())
        self.__room.setProperty(entity.Room.PROP_COLOR, self.__uiColor.text())
        self.__room.getView().update()