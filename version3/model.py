__author__ = 'thornag'

class Direction:
    N=1
    NE=2
    E=4
    SE=8
    S=16
    SW=32
    W=64
    NW=128

class Room:
    __exits=0
    __visited=False
    #some room settings
    def __init__(self, exits):
        self.__exits = exits

    def hasExit(self, exit_):
        return self.__exits & exit_

    def setVisited(self, bVisited):
        self.__visited = bool(bVisited)

    def isVisited(self):
        return bool(self.__visited)



class Map:
    def spawnRoom(self):
        #adds to room registry (this is room registry)
        pass

    def spawnLevel(self):
        #adds to level registry (this is level registry)
        pass

    def spawnLink(self):
        #addas to link registry (this is link registry)
        pass


