
from PyQt4 import QtGui, QtCore
import entity

class RoomProperties(QtCore.QObject):
    __uiRoomId=None
    __uiRoomName=None
    __uiCommands=None
    __uiColor=None
    __room=None
    def __init__(self, mainWindow):
        super(RoomProperties, self).__init__()
        self.__uiRoomId = mainWindow.uiPropertiesRoomId
        self.__uiRoomName = mainWindow.uiPropertiesRoomName
        self.__uiCommands = mainWindow.uiPropertiesCommands
        self.__uiColor = mainWindow.uiPropertiesColor
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

    def updateRoomFromProperties(self):
        self.__room.setProperty(entity.Room.PROP_NAME, self.__uiRoomName.text())
        self.__room.setProperty(entity.Room.PROP_COMMANDS, self.__uiCommands.toPlainText())
        self.__room.setProperty(entity.Room.PROP_COLOR, self.__uiColor.text())
        self.__room.getView().update()