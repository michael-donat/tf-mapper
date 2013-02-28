import sys
from PyQt4 import QtCore
from PyQt4 import QtGui

def clicked():
    print "Button Clicked"

qApp = QtGui.QApplication(sys.argv)

button = QtGui.QPushButton("Click Me")
QtCore.QObject.connect(button, QtCore.SIGNAL('clicked()'), clicked)
button.show()

sys.exit(qApp.exec_())  