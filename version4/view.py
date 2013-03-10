
from PyQt4 import uic, QtGui, QtCore
import di, model.model as model
import json, base64
import types
import roomClasses

import icons_rc

window, base = uic.loadUiType("ui/main.ui")

class uiMainWindow(window, base):
    __mapView=None
    __registry=di.ComponentRequest('Registry')
    __navigator=di.ComponentRequest('Navigator')
    __factory=di.ComponentRequest('RoomFactory')
    __clipboard=di.ComponentRequest('Clipboard')
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.__mapView = uiMapView()
        self.uiMapViewFrame.setLayout(QtGui.QVBoxLayout())
        self.uiMapViewFrame.layout().addWidget(self.__mapView)
        self.__mapView.show()

    def hidePanels(self):
        self.uiComponentToolsPanel.hide()
        self.uiComponentPropertiesPanel.hide()

    def buildClasses(self, classes):
        self.uiCreationClass.addItem('')
        self.uiPropertiesClass.addItem('')
        for function in dir(classes):
            if isinstance(classes.__dict__.get(function), types.FunctionType):
                self.uiCreationClass.addItem(function)
                self.uiPropertiesClass.addItem(function)


    def setKeepOnTop(self, keep):
        if keep:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def mapView(self):
        return self.__mapView

    def keyPressEvent(self, QKeyEvent):

        if QKeyEvent.key() in [QtCore.Qt.Key_Insert, QtCore.Qt.Key_Equal, QtCore.Qt.Key_Slash]:
            self.__registry.roomShadow.stopProcess()
            self.walkerModeSelector.setCurrentIndex(int(not self.walkerModeSelector.currentIndex()))

        if QKeyEvent.key() == QtCore.Qt.Key_Asterisk:
            self.__registry.roomShadow.stopProcess()
            self.autoPlacement.setChecked(not self.autoPlacement.isChecked())

        if QKeyEvent.key() == QtCore.Qt.Key_Shift:
            self.__mapView.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.__registry.roomShadow.stopProcess()

        if QKeyEvent.key() in [QtCore.Qt.Key_Enter]:
            self.__registry.roomShadow.finaliseProcess()

        if QKeyEvent.key() == QtCore.Qt.Key_Return:
            self.compassPlace.click()

        if QKeyEvent.key() == QtCore.Qt.Key_Delete:
            self.__navigator.removeRoom()

        if QKeyEvent.matches(QtGui.QKeySequence.Copy):
            QRectF = QtCore.QRectF()
            items = self.mapView().scene().selectedItems()
            for item in items:
                QRectF = QRectF.united(item.sceneBoundingRect())
            self.__clipboard.copyRooms(self.mapView().scene(), QRectF)

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Shift:
            self.__mapView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

class uiMapLevel(QtGui.QGraphicsScene):
    __model=None
    def __init__(self):
        super(uiMapLevel, self).__init__()
        self.setBackgroundBrush(QtGui.QColor(255, 255, 255, 127))

    def setModel(self, model):
        self.__model = model

    def getModel(self,):
        return self.__model


class uiMapView(QtGui.QGraphicsView):
    __coordinatesHelper=di.ComponentRequest('CoordinatesHelper')
    __roomFactory=di.ComponentRequest('RoomFactory')
    __registry=di.ComponentRequest('Registry')
    __map=di.ComponentRequest('Map')

    def setScene(self, scene):

        x1 = x2 = y1 = y2 = 0

        for key, level in self.__map.levels().items():
            sceneRect = level.getView().sceneRect()
            x1 = sceneRect.left() if sceneRect.left() < x1 else x1
            x2 = sceneRect.right() if sceneRect.right() > x2 else x2
            y1 = sceneRect.top() if sceneRect.top() < y1 else y1
            y2 = sceneRect.bottom() if sceneRect.bottom() > y2 else y2

        newQRectF = QtCore.QRectF()
        newQRectF.setLeft(x1)
        newQRectF.setTop(y1)
        newQRectF.setRight(x2)
        newQRectF.setBottom(y2)

        for key, level in self.__map.levels().items():
            level.getView().setSceneRect(newQRectF)

        self.__registry.currentLevel=scene.getModel()
        super(uiMapView, self).setScene(scene)

    def coordinatesHelper(self):
        return self.__coordinatesHelper

    def roomFactory(self):
        return self.__roomFactory

    def __init__(self):
        super(uiMapView, self).__init__()
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)


    def contextMenuEvent(self, event):
        eventPos = event.pos()
        menu = QtGui.QMenu()
        action = QtGui.QAction(str.format('Add room at {0}x{1}', eventPos.x(), eventPos.y()), self)

        createAt = self.coordinatesHelper().centerFrom(self.mapToScene(eventPos))

        action.triggered.connect(lambda: self.roomFactory().createAt(createAt, self.scene()))

        menu.addAction(action)

        action = QtGui.QAction(str.format('Paste at {0}x{1}', eventPos.x(), eventPos.y()), self)
        action.setDisabled(True)
        if QtGui.QApplication.clipboard().text():
            action.setDisabled(False)
            action.triggered.connect(lambda: self.roomFactory().pasteAt(createAt, self.scene(), json.loads(base64.standard_b64decode(QtGui.QApplication.clipboard().text()))))
        menu.addAction(action)

        action = QtGui.QAction(str.format('Create label at {0}x{1}', eventPos.x(), eventPos.y()), self)
        action.triggered.connect(lambda: self.roomFactory().createLabelAt(createAt, self.scene()))
        menu.addAction(action)


        menu.exec_(event.globalPos())
        event.accept()

class Link(QtGui.QGraphicsLineItem):
    __coordinateshelper=di.ComponentRequest('CoordinatesHelper')
    __model=None

    def __init__(self):
        super(Link, self).__init__()

    def setModel(self, model):
        self.__model = model

    def getModel(self,):
        return self.__model

    def redraw(self):
        startPoint = self.__coordinateshelper.getExitPoint(self.getModel().getLeft())
        endPoint = self.__coordinateshelper.getExitPoint(self.getModel().getRight())
        self.setLine(startPoint.x(), startPoint.y(), endPoint.x(), endPoint.y())
        isUpDown = self.getModel().getLeft()[1] in [model.Direction.U, model.Direction.D] or self.getModel().getRight()[1] in [model.Direction.U, model.Direction.D]
        if self.getModel().isCustom() or isUpDown:
            pen = QtGui.QPen(QtCore.Qt.DashDotDotLine)
            self.setPen(pen)
        else:
            self.setPen(QtGui.QPen(QtCore.Qt.SolidLine))
        self.setZValue(-1)
        self.update()

class ShadowLink(QtGui.QGraphicsLineItem):
    __registry=di.ComponentRequest('Registry')
    __coordinateshelper=di.ComponentRequest('CoordinatesHelper')
    def __init__(self):
        super(ShadowLink, self).__init__()
    def redraw(self):
        startPoint = self.__coordinateshelper.getExitPoint((self.__registry.currentlyVisitedRoom, self.__registry.roomShadow.exitBy(), None))
        endPoint = self.__coordinateshelper.getExitPointFromPoint(self.__registry.roomShadow.pos(), self.__registry.roomShadow.entryBy())
        self.setLine(startPoint.x(), startPoint.y(), endPoint.x(), endPoint.y())
        self.update()

class RoomShadow(QtGui.QGraphicsItem):
    __config = di.ComponentRequest('Config')
    __registry=di.ComponentRequest('Registry')
    __navigator=di.ComponentRequest('Navigator')
    __inProcess=False
    __exitBy=None
    __entryBy=None
    def __init__(self):
        super(RoomShadow, self).__init__()
        self.__boundingRect = QtCore.QRectF(0,0,self.__config.getSize(),self.__config.getSize())

    def stopProcess(self):
        self.__registry.shadowLink.setVisible(False)
        self.setInProcess(False)
        self.setVisible(False)

    def setInProcess(self, inProcess):
        self.__inProcess = bool(inProcess)

    def inProcess(self):
        return self.__inProcess

    def setExitBy(self, exit):
        self.__exitBy = exit

    def exitBy(self):
        return self.__exitBy

    def setEntryBy(self, exit):
        self.__entryBy = exit

    def entryBy(self):
        return self.__entryBy

    def boundingRect(self):
        return self.__boundingRect

    def finaliseProcess(self):
        if not self.inProcess(): return
        self.__navigator.dropRoomFromShadow()
        self.stopProcess()
        #print 'fired priocess'

    def paint(self, painter, option, widget):

        objectSize = self.__config.getSize()

        painter.setPen(QtCore.Qt.DashLine)
        painter.drawRect(0,0,objectSize,objectSize)

class Room(QtGui.QGraphicsItem):
    __boundingRect=None
    __config = di.ComponentRequest('Config')
    __registry= di.ComponentRequest('Registry')
    __navigator= di.ComponentRequest('Navigator')
    __coordinatesHelper = di.ComponentRequest('CoordinatesHelper')
    __model = None
    __factory=di.ComponentRequest('RoomFactory')
    def __init__(self):
        super(Room, self).__init__()
        self.__boundingRect = QtCore.QRectF(0,0,self.__config.getSize(),self.__config.getSize())

        self.color = self.defColor = QtGui.QColor(100,100,100)

        self.setFlags(QtGui.QGraphicsItem.ItemSendsGeometryChanges | QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable)

        #self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)

    def setModel(self, model):
        self.__model = model

    def getModel(self,):
        return self.__model

    def boundingRect(self):
        return self.__boundingRect

    def paint(self, painter, option, widget):
        self.color = self.defColor
        if self.getModel().getProperty(model.Room.PROP_COLOR) is not None:
            color = QtGui.QColor()
            color.setNamedColor(self.getModel().getProperty(model.Room.PROP_COLOR))
            if color.isValid():
                self.color = color

        className = self.getModel().getProperty(model.Room.PROP_CLASS)

        if className in dir(roomClasses):
            function = roomClasses.__dict__.get(className)
            function(self)

        objectSize = self.__config.getSize()
        edgeSize = self.__config.getEdgeLength()
        exitSize = self.__config.getExitLength()
        midPoint = self.__config.getMidPoint()

        if self.isSelected():
            painter.setPen(QtCore.Qt.DashLine)
            painter.drawRect(0,0,objectSize,objectSize)
        else:
            painter.setPen(QtCore.Qt.SolidLine)

        if self.__model.isCurrentlyVisited():
            currentColor = QtGui.QColor(255,255,255)
            painter.setBrush(currentColor)
            if self.isSelected():
                painter.setPen(QtCore.Qt.DashLine)
            painter.drawEllipse(0,0,objectSize,objectSize)

        currentColor = self.color
        painter.setBrush(self.color)

        painter.setPen(QtCore.Qt.SolidLine)
        painter.drawRect(exitSize, exitSize, edgeSize, edgeSize)

        if self.__model.hasExit(model.Direction.N):
            painter.drawLine(midPoint, 0, midPoint, exitSize)

        if self.__model.hasExit(model.Direction.NE):
            painter.drawLine(exitSize + edgeSize, exitSize, objectSize, 0)

        if self.__model.hasExit(model.Direction.E):
            painter.drawLine(exitSize + edgeSize, midPoint, objectSize, midPoint)

        if self.__model.hasExit(model.Direction.SE):
            painter.drawLine(exitSize + edgeSize, exitSize + edgeSize, objectSize, objectSize)

        if self.__model.hasExit(model.Direction.S):
            painter.drawLine(midPoint, exitSize + edgeSize, midPoint, objectSize)

        if self.__model.hasExit(model.Direction.SW):
            painter.drawLine(0, objectSize, exitSize, exitSize + edgeSize)

        if self.__model.hasExit(model.Direction.W):
            painter.drawLine(0, midPoint, exitSize, midPoint)

        if self.__model.hasExit(model.Direction.NW):
            painter.drawLine(0, 0, exitSize, exitSize)

        if self.__model.hasExit(model.Direction.U):
            #if self.__model.isCurrentlyVisited(): painter.setBrush(QtGui.QColor(100,100,100))
            #else: painter.setBrush(QtGui.QColor(255,255,255))
            painter.setBrush(QtGui.QColor(255,255,255))
            painter.setPen(QtCore.Qt.NoPen)
            QRect = QtCore.QRectF(exitSize, exitSize, edgeSize, edgeSize/2)
            QRect.adjust(edgeSize/float(5),edgeSize/10,-1*edgeSize/5,-1*edgeSize/10)
            painter.drawRect(QRect)

        if self.__model.hasExit(model.Direction.D):
            #if self.__model.isCurrentlyVisited(): painter.setBrush(QtGui.QColor(100,100,100))
            #else: painter.setBrush(QtGui.QColor(255,255,255))
            painter.setBrush(QtGui.QColor(255,255,255))
            painter.setPen(QtCore.Qt.NoPen)
            QRect = QtCore.QRectF(exitSize, midPoint, edgeSize, edgeSize/2)
            QRect.adjust(edgeSize/float(5),edgeSize/10,-1*edgeSize/5,-1*edgeSize/10)
            painter.drawRect(QRect)

        label = self.__model.getProperty(model.Room.PROP_LABEL)
        if len(label):
            font = QtGui.QFont(QtGui.QApplication.font())
            font.setPointSize(font.pointSize()*1.3)
            font.setWeight(100)
            painter.setFont(font)
            label= label.rjust(2,' ')
            label = label.ljust(3,' ')
            painter.setPen(QtGui.QColor(0,0,0))
            painter.drawText(QtCore.QPointF(exitSize+1,exitSize+edgeSize-5),label)

    #def mousePressEvent(self, QGraphicsSceneMouseEvent):
    #    print QGraphicsSceneMouseEvent.modifiers() & QtCore.Qt.ShiftModifier
    #    if not QGraphicsSceneMouseEvent.modifiers() & QtCore.Qt.ShiftModifier:
    #        for item in self.scene().selectedItems():
    #            item.setSelected(False)#
    #
    #    self.setSelected(True)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
       self.__navigator.markVisitedRoom(self.__model)

    def itemChange(self, QGraphicsItem_GraphicsItemChange, QVariant):
        if QGraphicsItem_GraphicsItemChange == QtGui.QGraphicsItem.ItemPositionChange:
            return self.__coordinatesHelper.snapToGrid(QVariant.toPoint())

        if QGraphicsItem_GraphicsItemChange == QtGui.QGraphicsItem.ItemPositionHasChanged:
            self.getModel().setPositionFromView()
            links = self.getModel().getLinks()
            for link in links:
                if links[link].isCustom(): continue
                if links[link].getView():
                    links[link].getView().redraw()
            links = self.getModel().getCustomLinks()
            for link in links:
                if link.getView():
                    link.getView().redraw()

        return super(Room, self).itemChange(QGraphicsItem_GraphicsItemChange, QVariant)

class Label(QtGui.QGraphicsTextItem):
    def __init__(self, text):
        super(Label, self).__init__(text)
        font = QtGui.QFont(QtGui.QApplication.font())
        font.setPointSize(font.pointSize()*1.4)
        self.setFont(font)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction);

    def focusOutEvent(self, QFocusEvent):
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction);