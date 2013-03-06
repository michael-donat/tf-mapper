__author__ = 'thornag'

from PyQt4 import QtNetwork, QtCore

class Broadcaster(QtCore.QObject):
    __tcpServer=None
    __clientSocket=None
    dataReceived=QtCore.pyqtSignal(str)
    def __init__(self, port):
        super(Broadcaster, self).__init__()

        self.__clients = []

        self.__tcpServer = QtNetwork.QTcpServer()
        if not self.__tcpServer.listen(QtNetwork.QHostAddress.LocalHost, port):
            raise Exception('Could not initialize socket server.')
        else:
            pass
            #print 'Server listening on %s' % port

        self.__tcpServer.newConnection.connect(self.registerClient)

        #print self.__tcpServer

    def tcpServer(self):
        return self.__tcpServer

    def registerClient(self):
        clientSocket = self.__tcpServer.nextPendingConnection()
        clientSocket.readyRead.connect(lambda: self.readClient(clientSocket))
        self.killOldConnection()
        self.__clientSocket = clientSocket

    def killOldConnection(self):
        if not self.__clientSocket: return
        self.__clientSocket.write('New connection received. Closing link...\n')
        self.__clientSocket.close()

    def readClient(self, clientSocket):
        data = clientSocket.readAll()
        self.dataReceived.emit(data.trimmed().data())


