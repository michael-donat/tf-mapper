__author__ = 'donatm'


class Room(object):
    __properties=None
    def __init__(self):
        self.__properties = Properties()

    def getProperties(self):
        return self.__properties


class Properties(object):
    __name=None
    __label=None
    __description=None
    __textReturn=None
    __terrainClass=None
    __color=None

    def name(self): return self.__name
    def label(self): return self.__label
    def description(self): return self.__description
    def textReturn(self): return self.__textReturn
    def terrainClass(self): return self.__terrainClass
    def color(self): return self.__color

    def setName(self, name):
        self.__name = name

    def setLabel(self, label):
        self.__label = label

    def setDescription(self, description):
        self.__description = description

    def setTextReturn(self, textReturn):
        self.__textReturn = textReturn

    def setTerrainClass(self, terrainClass):
        self.__terrainClass = terrainClass

    def setColor(self, color):
        self.__color = color

class Exits(object):
    pass

class Exit(object):
    pass

class Geometry(object):
    pass
