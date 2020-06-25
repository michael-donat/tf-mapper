__author__ = 'thornag'

from PyQt5 import QtNetwork, QtCore

class Listener(QtCore.QObject):
    __tcpSocket=None
    dataReceived=QtCore.pyqtSignal(str)
    def __init__(self, port):
        super(Listener, self).__init__()

        self.__tcpSocket = QtNetwork.QTcpSocket()
        self.__tcpSocket.connectToHost("localhost",9999)

        self.__tcpSocket.newConnection.connected(self.startListening)

        #print(self.__tcpServer)

    def startListening(self):
        self.__tcpSocket.readyRead.connect(self.read)

    def read(self):
        data = self.__tcpSocket.readAll()
        self.dataReceived.emit(data.trimmed().data())


