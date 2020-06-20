
from PyQt5 import uic, QtGui, QtCore, QtOpenGL, QtWidgets
import di, model.model as model
import json, base64
import types
import roomClasses
import os, sys
import math

import icons_rc


uipath = os.path.abspath('ui/main.ui')

window, base = uic.loadUiType(uipath)

class uiMainWindow(window, base):
    __mapView=None
    __registry=di.ComponentRequest('Registry')
    __navigator=di.ComponentRequest('Navigator')
    __factory=di.ComponentRequest('RoomFactory')
    __clipboard=di.ComponentRequest('Clipboard')
    __displayHelper=1
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.__mapView = uiMapView()
        self.__mapView.enableAntialiasing(True)

        self.uiMapViewFrame.setLayout(QtWidgets.QVBoxLayout())
        self.uiMapViewFrame.layout().addWidget(self.__mapView)
        #self.switchDisplaying()
        self.__mapView.show()
        self.menuActionEnableAntialiasing.toggled.connect(self.__mapView.enableAntialiasing)
        #self.pushButtonDebug.clicked.connect(self.switchDisplaying)

    def switchDisplaying(self):
        self.__displayHelper += 1
        if self.__displayHelper == 1:
            self.__mapView.setViewport(QtOpenGL.QGLWidget(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)))
        if self.__displayHelper == 2:
            self.__mapView.setViewport(QtOpenGL.QGLWidget(QtOpenGL.QGLFormat()))
        if self.__displayHelper == 3:
            self.__mapView.setViewport(QtGui.QWidget())
            self.__displayHelper = 0

    def hidePanels(self):
        self.uiComponentToolsPanel.hide()
        self.uiComponentPropertiesPanel.hide()

    def buildShortcuts(self, shortcuts):
        menubar = self.menuBar
        fileMenu = menubar.addMenu('Shortcuts')
        shorts = shortcuts.shortcuts()
        for room in shorts:
            exitAction = QtWidgets.QAction(room['name'], fileMenu)
            exitAction.setToolTip(room['room'])
            exitAction.triggered.connect(lambda dummy, roomId=room['room']: self.__navigator.viewRoom(roomId))
            fileMenu.addAction(exitAction)


    def buildClasses(self, classes):
        self.uiCreationClass.addItem('')
        self.uiPropertiesClass.addItem('')
        for function in dir(classes):
            if isinstance(classes.__dict__.get(function), types.FunctionType):
                self.uiCreationClass.addItem(function)
                self.uiPropertiesClass.addItem(function)


    def setKeepOnTop(self, keep):
        if keep:
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
        self.show()

    def mapView(self):
        return self.__mapView

    def keyPressEvent(self, QKeyEvent):

        if QKeyEvent.key() in [QtCore.Qt.Key_Insert, QtCore.Qt.Key_Equal, QtCore.Qt.Key_Slash]:
            if self.uiComponentToolsPanel.isVisible():
                self.__registry.roomShadow.stopProcess()
                self.walkerModeSelector.setCurrentIndex(int(not self.walkerModeSelector.currentIndex()))

        if QKeyEvent.key() == QtCore.Qt.Key_Asterisk:
            self.__registry.roomShadow.stopProcess()
            self.autoPlacement.setChecked(not self.autoPlacement.isChecked())

        if QKeyEvent.key() == QtCore.Qt.Key_Shift:
            self.__mapView.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

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

        if QKeyEvent.matches(QtGui.QKeySequence.ZoomIn):
            self.__registry.zoonInFunction()

        if QKeyEvent.matches(QtGui.QKeySequence.ZoomOut):
            self.__registry.zoonOutFunction()

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Shift:
            self.__mapView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

class uiMapLevel(QtWidgets.QGraphicsScene):
    __model=None
    def __init__(self):
        super(uiMapLevel, self).__init__()
        self.setBackgroundBrush(QtGui.QColor(255, 255, 255, 127))

    def setModel(self, model):
        self.__model = model

    def getModel(self,):
        return self.__model


class uiMapView(QtWidgets.QGraphicsView):
    __coordinatesHelper=di.ComponentRequest('CoordinatesHelper')
    __roomFactory=di.ComponentRequest('RoomFactory')
    __registry=di.ComponentRequest('Registry')
    __map=di.ComponentRequest('Map')

    def enableAntialiasing(self, Enable=True):
        if Enable:
            self.setRenderHints(QtGui.QPainter.RenderHints() | QtGui.QPainter.Antialiasing)
            self.update()
        else:
            self.setRenderHints(QtGui.QPainter.RenderHints())
            self.update()
        print(self.renderHints())

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
        #self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        #self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform | QtGui.QPainter.HighQualityAntialiasing | QtGui.QPainter.NonCosmeticDefaultPen)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        #self.setViewportUpdateMode(QtGui.QGraphicsView.MinimalViewportUpdate)

    def contextMenuEvent(self, event):
        eventPos = event.pos()
        menu = QtWidgets.QMenu()
        action = QtWidgets.QAction(str.format('Add room at {0}x{1}', eventPos.x(), eventPos.y()), self)

        createAt = self.coordinatesHelper().centerFrom(self.mapToScene(eventPos))

        action.triggered.connect(lambda: self.roomFactory().createAt(createAt, self.scene()))

        menu.addAction(action)

        action = QtWidgets.QAction(str.format('Paste at {0}x{1}', eventPos.x(), eventPos.y()), self)
        action.setDisabled(True)
        if QtWidgets.QApplication.clipboard().text():
            action.setDisabled(False)
            action.triggered.connect(lambda: self.roomFactory().pasteAt(createAt, self.scene(), json.loads(QtWidgets.QApplication.clipboard().text())))
        menu.addAction(action)

        action = QtWidgets.QAction(str.format('Create label at {0}x{1}', eventPos.x(), eventPos.y()), self)
        action.triggered.connect(lambda: self.roomFactory().createLabelAt(createAt, self.scene()))
        menu.addAction(action)


        menu.exec_(event.globalPos())
        event.accept()

class Link(QtWidgets.QGraphicsLineItem):
    __coordinateshelper=di.ComponentRequest('CoordinatesHelper')
    __model=None

    def __init__(self):
        super(Link, self).__init__()
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

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
            pen = QtGui.QPen(QtCore.Qt.DotLine)
            self.setPen(pen)
        else:
            self.setPen(QtGui.QPen(QtCore.Qt.SolidLine))
        self.setZValue(-1)
        self.update()

class ShadowLink(QtWidgets.QGraphicsLineItem):
    __registry=di.ComponentRequest('Registry')
    __coordinateshelper=di.ComponentRequest('CoordinatesHelper')
    def __init__(self):
        super(ShadowLink, self).__init__()
    def redraw(self):
        startPoint = self.__coordinateshelper.getExitPoint((self.__registry.currentlyVisitedRoom, self.__registry.roomShadow.exitBy(), None, None))
        endPoint = self.__coordinateshelper.getExitPointFromPoint(self.__registry.roomShadow.pos(), self.__registry.roomShadow.entryBy())
        self.setLine(startPoint.x(), startPoint.y(), endPoint.x(), endPoint.y())
        self.update()

class RoomShadow(QtWidgets.QGraphicsItem):
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
        #print('fired priocess')

    def paint(self, painter, option, widget):

        objectSize = self.__config.getSize()

        painter.setPen(QtCore.Qt.DashLine)
        painter.drawRect(0,0,objectSize,objectSize)

class Room(QtWidgets.QGraphicsItem):
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

        self.setFlags(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges | QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsFocusable)

        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)

    def setModel(self, model):
        self.__model = model

    def getModel(self,):
        return self.__model

    def boundingRect(self):
        return self.__boundingRect

    def drawArrowHead(self, line, painter):

        brush = painter.brush()
        d = self.__config.getExitLength()
        theta = math.pi / 7

        lineAngle = math.atan2(line.dy(), line.dx())
        h = math.fabs(d/math.cos(theta))

        angle1 = lineAngle + theta
        angle2 = lineAngle - theta

        angle1 = math.pi + lineAngle + theta
        angle2 = math.pi + lineAngle - theta

        P1 = QtCore.QPointF(line.x2()+math.cos(angle1)*h,line.y2()+math.sin(angle1)*h)
        P2 = QtCore.QPointF(line.x2()+math.cos(angle2)*h,line.y2()+math.sin(angle2)*h)

        painter.setBrush(QtGui.QColor(0,0,0))
        painter.drawPolygon(line.p2(), P1, P2)
        painter.setBrush(brush)

    def paint(self, painter, option, widget):

        """cacheExitString = ""
        cacheString = "StorageKey-color:%s-class:%s-selected:%s-visited:%s-disabled:%s-label:%s-exits:%s"

        for exitDir in model.Direction.getAllAsList():
            if self.__model.hasExit(exitDir):
                cacheExitString += str(exitDir)
                link = self.__model.linkAt(exitDir)
                sourceSide = link.getSourceSideFor(self.__model)
                if sourceSide[3] is not None and len(sourceSide[3]) and sourceSide[3] == 'N/A':
                    cacheExitString += ".|"
                else:
                    cacheExitString += "|"

        cacheString = cacheString % (   self.getModel().getProperty(model.Room.PROP_COLOR),
                                        self.getModel().getProperty(model.Room.PROP_CLASS),
                                        self.isSelected(),
                                        self.__model.isCurrentlyVisited(),
                                        self.getModel().getProperty('disabled'),
                                        self.__model.getProperty(model.Room.PROP_LABEL),
                                        cacheExitString)

        pixmap = QtGui.QPixmapCache.find(cacheString)

        if pixmap is None:
            pixmap = self.generatePixmap(painter, option, widget)
            QtGui.QPixmapCache.insert(cacheString, pixmap)"""

        self.generatePixmap(painter, option, widget)


    def generatePixmap(self, painter, option, widget):

        #pixmap = QtGui.QPixmap(self.__config.getSize(), self.__config.getSize())
        #painter = QtGui.QPainter(pixmap)

        #painter.drawRect(0, 0, self.__config.getSize(), self.__config.getSize())

        self.color = self.defColor
        if self.__registry.applyColors and self.getModel().getProperty(model.Room.PROP_COLOR) is not None:
            color = QtGui.QColor()
            color.setNamedColor(self.getModel().getProperty(model.Room.PROP_COLOR))
            if color.isValid():
                self.color = color

        className = self.getModel().getProperty(model.Room.PROP_CLASS)

        if self.__registry.applyClasses and className in dir(roomClasses):
            function = roomClasses.__dict__.get(className)
            function(self)

        objectSize = self.__config.getSize()
        edgeSize = self.__config.getEdgeLength()
        exitSize = self.__config.getExitLength()
        midPoint = self.__config.getMidPoint()

        if self.getModel().isHighlighted():
            painter.setBrush(QtCore.Qt.yellow)
            painter.drawEllipse(0,0,objectSize,objectSize)

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


        if self.getModel().getProperty('disabled'):
            currentColor = QtGui.QColor(255,255,255, 50)
            painter.setBrush(currentColor)
        else:
            painter.setPen(QtCore.Qt.SolidLine)

        painter.drawRect(exitSize, exitSize, edgeSize, edgeSize)

        if self.__model.hasExit(model.Direction.N):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.N)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(midPoint, 0, midPoint, exitSize)
            if sourceSide[3] is not None and len(sourceSide[3]):
                 if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                 else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(midPoint, 0, midPoint, exitSize)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.NE):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.NE)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(objectSize, 0, exitSize + edgeSize, exitSize)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(exitSize + edgeSize, exitSize, objectSize, 0)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.E):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.E)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(objectSize, midPoint, exitSize + edgeSize, midPoint)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(exitSize + edgeSize, midPoint, objectSize, midPoint)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.SE):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.SE)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(objectSize, objectSize, exitSize + edgeSize, exitSize + edgeSize)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(exitSize + edgeSize, exitSize + edgeSize, objectSize, objectSize)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.S):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.S)
            sourceSide = link.getSourceSideFor(self.__model)
            line=QtCore.QLineF(midPoint, objectSize, midPoint, exitSize + edgeSize)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(line)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.SW):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.SW)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(0, objectSize, exitSize, exitSize + edgeSize)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(0, objectSize, exitSize, exitSize + edgeSize)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.W):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.W)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(0, midPoint, exitSize, midPoint)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(0, midPoint, exitSize, midPoint)
            painter.setPen(pen)

        if self.__model.hasExit(model.Direction.NW):
            pen = painter.pen()
            link = self.__model.linkAt(model.Direction.NW)
            sourceSide = link.getSourceSideFor(self.__model)
            line = QtCore.QLineF(0, 0, exitSize, exitSize)
            if sourceSide[3] is not None and len(sourceSide[3]):
                if sourceSide[3] == 'N/A':
                    self.drawArrowHead(line, painter)
                else:
                    newpen = QtGui.QPen(pen)
                    newpen.setColor(QtGui.QColor(9,171,235))
                    painter.setPen(newpen)
            painter.drawLine(0, 0, exitSize, exitSize)
            painter.setPen(pen)

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
            font = QtGui.QFont(QtWidgets.QApplication.font())
            font.setPointSize(font.pointSize()*1.3)
            font.setWeight(80)
            painter.setFont(font)
            label= label.rjust(2,' ')
            label = label.ljust(3,' ')
            painter.setPen(QtGui.QColor(0,0,0))
            painter.drawText(QtCore.QPointF(exitSize+1,exitSize+edgeSize-5),label)

        #return pixmap

    #def mousePressEvent(self, QGraphicsSceneMouseEvent):
    #    print(QGraphicsSceneMouseEvent.modifiers() & QtCore.Qt.ShiftModifier)
    #    if not QGraphicsSceneMouseEvent.modifiers() & QtCore.Qt.ShiftModifier:
    #        for item in self.scene().selectedItems():
    #            item.setSelected(False)#
    #
    #    self.setSelected(True)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
       self.__navigator.markVisitedRoom(self.__model)

    def itemChange(self, QGraphicsItem_GraphicsItemChange, QVariant):
        if QGraphicsItem_GraphicsItemChange == QtWidgets.QGraphicsItem.ItemPositionChange:
            originPoint = QVariant.toPoint()
            if  abs(originPoint.x() - self.getModel().position().x()) > (2 * self.__config.getSize()) or \
                abs(originPoint.y() - self.getModel().position().y()) > (2 * self.__config.getSize()):
                return self.getModel().position()

            return self.__coordinatesHelper.snapToGrid(QVariant.toPoint())

        if QGraphicsItem_GraphicsItemChange == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
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

class Label(QtWidgets.QGraphicsTextItem):
    def __init__(self, text):
        super(Label, self).__init__(text)
        font = QtGui.QFont()
        font.setHintingPreference(QtGui.QFont.PreferFullHinting | QtGui.QFont.PreferQuality)
        font.setPixelSize(20)
        self.setFont(font)


    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction);

    def focusOutEvent(self, QFocusEvent):
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction);