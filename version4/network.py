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
        print 'RECEIVED: %s' % data

    def send(self, data):
        print 'SENDING: %s' % data
        if self.__clientSocket is not None:
            self.__clientSocket.write(data)

class Listener(QtCore.QObject):
    __tcpSocket=None
    dataReceived=QtCore.pyqtSignal(str)
    def __init__(self, host, port):
        super(Listener, self).__init__()

        self.__tcpSocket = QtNetwork.QTcpSocket()
        self.__tcpSocket.connectToHost(host,port)

        self.__tcpSocket.connected.connect(self.startListening)
        self.__tcpSocket.error.connect(self.notifyError)

        #print self.__tcpServer

    def startListening(self):
        self.__tcpSocket.readyRead.connect(self.read)

    def notifyError(self):
        print 'could not connect socket'

    def read(self):
        data = self.__tcpSocket.readAll()
        self.dataReceived.emit(data.trimmed().data())

    def send(self, data):
        self.__tcpSocket.write(data)

