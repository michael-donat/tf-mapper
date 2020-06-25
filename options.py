import sys, getopt
from PyQt5 import QtCore

def getOptions():
    opts, args = getopt.getopt(sys.argv[1:], "rm:", ["map=", "remote", "disable-connectivity", "panels", "no-panels", "key-up=", "key-down=", "width=", "height=", "room="])

    spawnRemoteConnection = False
    noServer = False
    mapFile='map.db'
    noPanels=False
    width=0
    height=0
    room=None

    keyUp = '.'
    keyDown = '0'

    settings = QtCore.QSettings('MudMapper', 'net.michaeldonat')

    width = int(settings.value('width', 0))
    height = int(settings.value('height', 0))
    noServer = True if settings.value('server') == "true" else False
    noPanels = True if settings.value('panels') == "true" else False
    room = settings.value('room', None)
    mapFile = settings.value('map', None)


    for opt, arg in opts:
        if opt in ("-m", "--map"):
            mapFile=arg
        if opt in ("-r", "--remote"):
            spawnRemoteConnection = True
        if opt == "--disable-connectivity":
            noServer = True
        if opt == "--no-panels":
            noPanels = True
        if opt == '--key-down':
            keyDown = arg
        if opt == '--key-up':
            keyUp = arg
        if opt == '--width':
            width = arg
        if opt == '--height':
            height = arg
        if opt == '--room':
            room = arg
        if opt == "--panels":
            noPanels = False

    options =  Options(spawnRemoteConnection,
        noServer,
        mapFile,
        noPanels,
        width,
        height,
        room,
        keyUp,
        keyDown
    )

    return options

class Options(object):
    spawnRemoteConnection=None
    noServer=None
    mapFile=None
    noPanels=None
    width=None
    height=None
    room=None
    keyUp=None
    keyDown=None

    def __init__(self,spawnRemoteConnection,noServer,mapFile,noPanels,width,height,room,keyUp,keyDown):
        self.spawnRemoteConnection = spawnRemoteConnection
        self.noServer = noServer
        self.mapFile=mapFile
        self.noPanels=noPanels
        self.width=width
        self.height=height
        self.room=room
        self.keyUp=keyUp
        self.keyDown=keyDown

