__author__ = 'donatm'


class Geometry(object):
    configMidPoint = 0
    configBoxSize = 0
    def __init__(self, configuration):
        self.configBoxSize = configuration.getBoxSize()
        self.configMidPoint = configuration.getMidPoint()

    def snapToGrid(self, QFPoint):
        x = int(QFPoint.x() / self.configBoxSize) * self.configBoxSize
        y = int(QFPoint.y() / self.configBoxSize) * self.configBoxSize

        if abs(QFPoint.x()) % self.configBoxSize > self.configMidPoint:
            if(QFPoint.x() < 0):
                x -= self.configBoxSize
            else:
                x += self.configBoxSize

        if abs(QFPoint.y()) % self.configBoxSize > self.configMidPoint:
            if(QFPoint.y() < 0):
                y -= self.configBoxSize
            else:
                y += self.configBoxSize

        QFPoint.setX(x)
        QFPoint.setY(y)

        return QFPoint