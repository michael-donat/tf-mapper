
from PyQt4 import QtGui, QtCore
import entity
import model
import di


class PropertiesExitsTableModel(QtCore.QAbstractTableModel):
    COLUMN_GO_BUTTON=0
    COLUMN_DIRECTION=1
    COLUMN_LABEL=2
    COLUMN_REBIND=3
    COLUMN_DESTINATION=4
    COLUMN_REMOVE_BUTTON=5
    __map=di.ComponentRequest('Map')
    __navigator=di.ComponentRequest('Navigator')
    __room=None
    def __init__(self, roomModel):
        super(PropertiesExitsTableModel, self).__init__()
        self.__room = roomModel


    def getItems(self):
        items = set(self.__room.getLinks().values()+self.__room.getCustomLinks())
        return list(items)


    def rowCount(self, QModelIndex):
        items = set(self.__room.getLinks().values()+self.__room.getCustomLinks())
        return len(items)
    def columnCount(self, QModelIndex):
        #1-exit, 2-label, 3-destination
        return 6
    def data(self, QModelIndex, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            items = set(self.__room.getLinks().values()+self.__room.getCustomLinks())
            items = list(items)
            link = items[QModelIndex.row()]
            sourceSide = link.getSourceSideFor(self.__room)
            if QModelIndex.column() == self.COLUMN_GO_BUTTON:
                return 'GO'
            if QModelIndex.column() == self.COLUMN_DIRECTION:
                return model.Direction.mapToLabel(sourceSide[1])
            if QModelIndex.column() == self.COLUMN_LABEL:
                return sourceSide[2]
            if QModelIndex.column() == self.COLUMN_REBIND:
                return sourceSide[3]
            if QModelIndex.column() == self.COLUMN_DESTINATION:
                return link.getDestinationFor(self.__room).getId()
            if QModelIndex.column() == self.COLUMN_REMOVE_BUTTON:
                return 'REMOVE'
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == self.COLUMN_GO_BUTTON: return ''
                if section == self.COLUMN_DIRECTION: return 'dir'
                if section == self.COLUMN_LABEL: return 'follow'
                if section == self.COLUMN_REBIND: return 'rebind'
                if section == self.COLUMN_DESTINATION: return 'dest'
                if section == self.COLUMN_REMOVE_BUTTON: return 'rm'

    def setData(self, QModelIndex, data, role):
        if role == QtCore.Qt.EditRole:
            if QModelIndex.column() == self.COLUMN_LABEL:
                items = self.getItems()
                item = items[QModelIndex.row()]
                sourceSide = item.getSourceSideFor(self.__room)
                item.replaceSourceSideFor(self.__room, sourceSide[1], data.toString() if len(data.toString()) else None, sourceSide[3])
                return True
            if QModelIndex.column() == self.COLUMN_REBIND:
                items = self.getItems()
                item = items[QModelIndex.row()]
                sourceSide = item.getSourceSideFor(self.__room)
                item.replaceSourceSideFor(self.__room, sourceSide[1], sourceSide[2], data.toString() if len(data.toString()) else None)
                return True

    def flags(self, QModelIndex):
        flags =  QtCore.Qt.ItemIsEnabled
        if QModelIndex.column() == self.COLUMN_LABEL: flags = flags | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
        if QModelIndex.column() == self.COLUMN_REBIND: flags = flags | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
        return flags

    def doubleClicked(self, QModelIndex):
        if QModelIndex.column() == self.COLUMN_GO_BUTTON:
            roomId = str(self.index(QModelIndex.row(), self.COLUMN_DESTINATION).data().toString())
            self.__navigator.markVisitedRoom(self.__map.rooms()[roomId])
        if QModelIndex.column() == self.COLUMN_REMOVE_BUTTON:
            items = self.getItems()
            item = items[QModelIndex.row()]
            self.__room.deleteLink(item)


class RoomProperties(QtCore.QObject):
    __uiRoomId=None
    __uiRoomName=None
    __uiCommands=None
    __uiColor=None
    __uiClass=None
    __uiLabel=None
    __room=None
    __uiExitsTable=None
    def __init__(self, mainWindow):
        super(RoomProperties, self).__init__()
        self.__uiRoomId = mainWindow.uiPropertiesRoomId
        self.__uiRoomName = mainWindow.uiPropertiesRoomName
        self.__uiCommands = mainWindow.uiPropertiesCommands
        self.__uiColor = mainWindow.uiPropertiesColor
        self.__uiClass = mainWindow.uiPropertiesClass
        self.__uiLabel = mainWindow.uiPropertiesLabel
        self.__uiExitsTable = mainWindow.uiPropertiesExits
        self.__uiExitsTable.verticalHeader().hide()
        self.__uiExitsTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        mainWindow.uiPropertiesColorPicker.clicked.connect(self.pickColor)

        self.__uiRoomName.textEdited.connect(self.updateRoomFromProperties)
        self.__uiCommands.textChanged.connect(self.updateRoomFromProperties)
        self.__uiColor.textEdited.connect(self.updateRoomFromProperties)
        self.__uiLabel.textEdited.connect(self.updateRoomFromProperties)
        self.__uiClass.currentIndexChanged.connect(self.updateRoomFromProperties)

    def pickColor(self):
        color = self.__room.getProperty(model.Room.PROP_COLOR)
        if color is not None and len(color):
            QColor = QtGui.QColorDialog.getColor(QtGui.QColor(color))
        else:
            QColor = QtGui.QColorDialog.getColor()
        if not QColor.isValid(): return
        self.__uiColor.setText(str(QColor.name()))
        self.__uiColor.textEdited.emit('dummy')

    def updatePropertiesFromRoom(self, roomModel):

        self.__room = roomModel

        self.__uiRoomId.setText(roomModel.getId())
        self.__uiRoomName.setText(roomModel.getProperty('name') if roomModel.getProperty('name') is not None else '')
        self.__uiCommands.blockSignals(True)
        self.__uiCommands.setPlainText(roomModel.getProperty('commands') if roomModel.getProperty('commands') is not None else '')
        self.__uiCommands.blockSignals(False)
        self.__uiColor.setText(str(roomModel.getProperty('color')) if roomModel.getProperty('color') is not None else '')
        self.__uiLabel.setText(str(roomModel.getProperty('label')) if roomModel.getProperty('label') is not None else '')
        label = roomModel.getProperty('class')
        index = self.__uiClass.findText(str(label))
        self.__uiClass.blockSignals(True)
        if index != -1: self.__uiClass.setCurrentIndex(index)
        self.__uiClass.blockSignals(False)

        model = PropertiesExitsTableModel(roomModel)
        self.__uiExitsTable.setModel(model)
        self.__uiExitsTable.doubleClicked.connect(model.doubleClicked)
        #self.__uiExitsTable.clicked.connect(model.clicked)

        #for index in range(model.rowCount(None)):
        #    button = QtGui.QToolButton()
        #    button.setText(str(model.index(index, PropertiesExitsTableModel.COLUMN_DESTINATION).data().toString()))
        #    button.clicked.connect(lambda: self.__navigator.markVisitedRoom(self.__map.rooms()[str(model.index(index, PropertiesExitsTableModel.COLUMN_DESTINATION).data().toString())]))
        #    self.__uiExitsTable.setIndexWidget(model.index(index, PropertiesExitsTableModel.COLUMN_GO_BUTTON), button)


    def updateRoomFromProperties(self):
        self.__room.setProperty(entity.Room.PROP_NAME, str(self.__uiRoomName.text()) if len(self.__uiRoomName.text()) else None)
        self.__room.setProperty(entity.Room.PROP_COMMANDS, str(self.__uiCommands.toPlainText()) if len(self.__uiCommands.toPlainText()) else None)
        self.__room.setProperty(entity.Room.PROP_COLOR, str(self.__uiColor.text()) if len(self.__uiColor.text()) else None)
        self.__room.setProperty(entity.Room.PROP_LABEL, str(self.__uiLabel.text()) if len(self.__uiLabel.text()) else None)
        self.__room.setProperty(entity.Room.PROP_CLASS, str(self.__uiClass.currentText()) if len(self.__uiClass.currentText()) else None)
        self.__room.getView().update()