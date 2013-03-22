
import pytest
from model.tools import *

class TestTools:

    def test_enum(self):
        testEnum = enum('T1', 'T2', 'T3', 'T4', 'T5', 'T6')

        assert hasattr(testEnum, 'T1')
        assert hasattr(testEnum, 'T2')
        assert hasattr(testEnum, 'T3')

        assert 1 == testEnum.T1
        assert 2 == testEnum.T2
        assert 4 == testEnum.T3
        assert 8 == testEnum.T4
        assert 16 == testEnum.T5
        assert 32 == testEnum.T6
