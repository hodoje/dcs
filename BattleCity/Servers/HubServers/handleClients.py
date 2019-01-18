from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor


class DoesNothing(Protocol):
    pass


class HandleClientsFactory(Factory):
    def __init__(self, port, numberOfPlayers):
        self.hubsPort = port
        self.connections = 0
        self.maxConnections = numberOfPlayers
        self.buffer = []
        self.playerID = 'ID'
        self.playerID_iterator = 0

    def buildProtocol(self, addr):
        from Servers.HubServers import handshake
        if self.connections < self.maxConnections:
            return handshake.HandshakeFactory.buildProtocol(self, addr)

        protocol = DoesNothing()
        protocol.factory = Factory()
        return protocol

    def checkGameMode(self, gameMode):
        if self.maxConnections == gameMode and self.connections < self.maxConnections:
            return True
        else:
            return False

    def generatePlayerId(self):
        self.playerID_iterator += 1
        return self.playerID + str(self.playerID_iterator)


def handleConnection(port, gameMode, hubPipeEnd):
    pf = HandleClientsFactory(port, gameMode)
    reactor.listenTCP(port, pf)
    hubPipeEnd.send(pf)
    print('Started handling clients')
    #reactor.callLater(5, handshake.main, port)
    reactor.run()