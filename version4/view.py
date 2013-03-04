
from PyQt4 import uic, QtGui, QtCore
import di, model

window, base = uic.loadUiType("ui/main.ui")

class uiMainWindow(window, base):
    __mapView=None
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.__mapView = uiMapView()
        self.uiMapViewFrame.setLayout(QtGui.QVBoxLayout())
        self.uiMapViewFrame.layout().addWidget(self.__mapView)
        self.__mapView.show()

    def mapView(self):
        return self.__mapView

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Insert:
            print self.walkerModeSelector
            self.walkerModeSelector.setCurrentIndex(int(not self.walkerModeSelector.currentIndex()))

        if QKeyEvent.key() == QtCore.Qt.Key_Shift:
            self.__mapView.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Shift:
            self.__mapView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)






class uiMapLevel(QtGui.QGraphicsScene):
    def __init__(self):
        super(uiMapLevel, self).__init__()


class uiMapView(QtGui.QGraphicsView):
    __coordinatesHelper=di.ComponentRequest('CoordinatesHelper')
    __roomFactory=di.ComponentRequest('RoomFactory')

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
        menu.exec_(event.globalPos())

        event.accept()



class Room(QtGui.QGraphicsItem):
    __boundingRect=None
    __config = di.ComponentRequest('Config')
    __registry= di.ComponentRequest('Registry')
    __navigator= di.ComponentRequest('Navigator')
    __coordinatesHelper= di.ComponentRequest('CoordinatesHelper')
    __model=None
    def __init__(self):
        super(Room, self).__init__()
        self.__boundingRect = QtCore.QRectF(0,0,self.__config.getSize(),self.__config.getSize())

        self.color = QtGui.QColor(100,100,100)

        self.setFlags(QtGui.QGraphicsItem.ItemSendsGeometryChanges | QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable)

        #self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)

    def dropEvent(self, QGraphicsSceneDragDropEvent):
        print QGraphicsSceneDragDropEvent

    def setModel(self, model):
        self.__model = model

    def getModel(self,):
        return self.__model

    def boundingRect(self):
        return self.__boundingRect

    def paint(self, painter, option, widget):

        objectSize = self.__config.getSize()
        edgeSize = self.__config.getEdgeLength()
        exitSize = self.__config.getExitLength()
        midPoint = self.__config.getMidPoint()

        if self.isSelected():
            painter.setPen(QtCore.Qt.DashLine)
            painter.drawRect(0,0,objectSize,objectSize)

        painter.setPen(QtCore.Qt.SolidLine)

        if self.__model.isCurrentlyVisited():
            painter.setBrush(QtGui.QColor(255,255,255))
            painter.drawRect(0,0,objectSize,objectSize)
        else:
            painter.setBrush(self.color)

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

        #if QGraphicsItem_GraphicsItemChange == QtGui.QGraphicsItem.ItemPositionHasChanged:
        #    boundingRect = self.scene().itemsBoundingRect()
        #    boundingRect.adjust(-50,-50,50,50)
        #    self.scene().setSceneRect(boundingRect)

        return super(Room, self).itemChange(QGraphicsItem_GraphicsItemChange, QVariant)

