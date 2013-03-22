
import pytest

from model.room import *

from PyQt4 import QtCore, QtGui

class TestClassGeometry:

    def test_initMethod(self):
        assert QtCore.QPointF(0, 0) == Geometry().getPoint()

    def test_updateMethod(self):
        assert QtCore.QPointF(10, 10) == Geometry().update(10,10,0,0).getPoint()
        assert QtCore.QRectF(QtCore.QPointF(10, 10),  QtCore.QPointF(20, 20)) == Geometry().update(10,10,20,20).getRect()

        assert QtCore.QPointF(-13, -13) == Geometry().update(-13,-13,0,0).getPoint()
        assert QtCore.QRectF(QtCore.QPointF(-13, -13),  QtCore.QPointF(3, 3)) == Geometry().update(-13,-13,3,3).getRect()

    def test_updateFromPointMethod(self):
        with pytest.raises(RuntimeError):
            Geometry().updateFromPoint(QtCore.QPointF(10,10)).getPoint()

        geometry = Geometry()
        geometry.update(0,0,10,10) #needed x2/y2 to calculate widh height when updatig from points

        assert QtCore.QPointF(10, 10) == geometry.updateFromPoint(QtCore.QPointF(10,10)).getPoint()
        assert QtCore.QRectF(QtCore.QPointF(10, 10),  QtCore.QPointF(20, 20)) == geometry.updateFromPoint(QtCore.QPointF(10,10)).getRect()

        assert QtCore.QPointF(-10, -10) == geometry.updateFromPoint(QtCore.QPointF(-10,-10)).getPoint()
        assert QtCore.QRectF(QtCore.QPointF(-10, -10),  QtCore.QPointF(0, 0)) == geometry.updateFromPoint(QtCore.QPointF(-10,-10)).getRect()

    def test_updateFromRectMethod(self):

        assert QtCore.QRectF(QtCore.QPointF(15,15),QtCore.QPointF(25,25)) == Geometry().updateFromRect(QtCore.QRectF(15,15, 10, 10)).getRect()
        assert QtCore.QPointF(15,15) == Geometry().update(10, 10, 20, 20).updateFromRect(QtCore.QRectF(15,15, 10, 10)).getPoint()

        assert QtCore.QRectF(QtCore.QPointF(-15,-15),QtCore.QPointF(-5,-5)) == Geometry().updateFromRect(QtCore.QRectF(-15,-15, 10, 10)).getRect()
        assert QtCore.QPointF(-15,-15) == Geometry().updateFromRect(QtCore.QRectF(-15,-15, 10, 10)).getPoint()

    def test_updateFromViewMethod(self):

        QGraphicsItem = QtGui.QGraphicsRectItem(0,0,10,10)
        QGraphicsItem.moveBy(15, 15)


        assert QtCore.QRectF(QtCore.QPointF(15,15),QtCore.QPointF(25,25)) == Geometry().updateFromView(QGraphicsItem).getRect()
        assert QtCore.QPointF(15,15) == Geometry().updateFromView(QGraphicsItem).getPoint()

        QGraphicsItem.moveBy(-50, 0)

        assert QtCore.QRectF(QtCore.QPointF(-35,15),QtCore.QPointF(-25,25)) == Geometry().updateFromView(QGraphicsItem).getRect()
        assert QtCore.QPointF(-35,15) == Geometry().updateFromView(QGraphicsItem).getPoint()
