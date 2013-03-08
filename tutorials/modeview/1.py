__author__ = 'donatm'

import sys
from PyQt4 import QtGui, QtCore

class MyModel(QtCore.QAbstractTableModel):
    def rowCount(self, QModelIndex):
        return 2

    def columnCount(self, QModelIndex):
        return 3

    def data(self, QModelIndex, role):
        if role == QtCore.Qt.DisplayRole:
            return "Row %s, Column %s" % (QModelIndex.row(), QModelIndex.column())



app = QtGui.QApplication(sys.argv);
tableView = QtGui.QTableView()
myModel = MyModel()
tableView.setModel( myModel );
tableView.show()
sys.exit(app.exec_())

