from twisted.internet.protocol import Factory, Protocol
from twisted.internet import error


class HubProtocol(Protocol):
    def __init__(self, factory):
        self._factory = factory

    def connectionMade(self):
        _peer = self.transport.getPeer()
        print(f'Client {_peer.Host}:{_peer.Port} connected')
        self._factory.addConnection(self)

    def connectionLost(self, reason=error.ConnectionDone):
        if reason.check(error.ConnectionDone):
            print(reason.getErrorMessage())
        else:
            print("Connection violently broke: {}".format(reason.getErrorMessage()))

        self._factory.removeConnection(self)

    def dataReceived(self, data):
        print(data)
        self._factory.dataBuffer.append(data)


class HubFactory(Factory):
    def __init__(self):
        self._connections = []
        self.dataBuffer = []

    def buildProtocol(self, addr):
        return HubProtocol(self)

    def getConnections(self):
        return self._connections

    def addConnection(self, protocol):
        self._connections.append(protocol)

    def removeConnection(self, protocol):
        self._connections.remove(protocol)
