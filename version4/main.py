
import di
import view

from PyQt4 import QtGui, QtCore

if __name__ == '__main__':

    print di.container.register('RoomDrawer', view.Drawer())