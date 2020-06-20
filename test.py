import sys
from PyQt5 import QtGui, QtCore, QtWidgets


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.setGeometry(300, 300, 355, 280)
        self.setWindowTitle('Brushes')
        self.show()

    def paintEvent(self, e):
        import math
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor('#000000'))

        line = QtCore.QLineF(100,200,200,200)

        theta = math.pi / 8

        qp.drawLine(line)



        d = 5

        lineAngle = math.atan2(line.dy(), line.dx())
        h = math.fabs(d/math.cos(lineAngle))

        angle1 = math.pi + lineAngle + theta
        angle2 = math.pi + lineAngle - theta

        P1 = QtCore.QPointF(line.x2()+math.cos(angle1)*h,line.y2()+math.sin(angle1)*h)
        P2 = QtCore.QPointF(line.x2()+math.cos(angle2)*h,line.y2()+math.sin(angle2)*h)

        qp.drawPolygon(line.p2(), P1, P2)

        qp.end()
        

              
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    ex.show()
    ex.raise_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()