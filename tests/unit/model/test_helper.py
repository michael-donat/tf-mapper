
import pytest

from model.helper import Geometry
from PyQt4 import QtCore

@pytest.fixture
def ConfigFixture():
    class Config:
        def getBoxSize(self): return 21
        def getMidPoint(self): return 11
    return Config()


@pytest.fixture
def GeometryFixture(ConfigFixture):
    return Geometry(ConfigFixture)

class TestClassGeometry:

    def test_snapToGrid(self, GeometryFixture):

        assert QtCore.QPointF(0, 0) == GeometryFixture.snapToGrid(QtCore.QPointF(5, 5))
        assert QtCore.QPointF(21, 0) == GeometryFixture.snapToGrid(QtCore.QPointF(13, 5))
        assert QtCore.QPointF(21, 21) == GeometryFixture.snapToGrid(QtCore.QPointF(13, 17))
        assert QtCore.QPointF(0, 0) == GeometryFixture.snapToGrid(QtCore.QPointF(-5, -5))
        assert QtCore.QPointF(0, -21) == GeometryFixture.snapToGrid(QtCore.QPointF(-5, -13))
        assert QtCore.QPointF(-21, -21) == GeometryFixture.snapToGrid(QtCore.QPointF(-13, -17))
