from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol
from twisted.protocols import amp
from twisted.internet import reactor

from Servers.MasterServer import master
from Servers.HubServers import handshake


class GameRequest:
    def __init__(self, port=9050):
        self.port = port
        self.gameMode = 0
        self.givenID = ''
        self.deferred = None

    def initiate(self, gameMode):
        self.gameMode = gameMode
        point = TCP4ClientEndpoint(reactor, "localhost", self.port)
        self.deferred = connectProtocol(point, amp.AMP())
        self.deferred.addCallback(self.handshakeMaster)
        self.deferred.addCallback(self.recieveHubsPort)
        self.deferred.addCallback(self.applyNewPort)
        reactor.callLater(3, self.switchConnectionToHub)

    def handshakeMaster(self, ampProto):
        print('Handshaking master')
        gameMode = self.gameMode
        return ampProto.callRemote(master.ReceiveGameRequestHandler, gameMode=gameMode)

    def recieveHubsPort(self, result):
        return result['hubPort']

    def applyNewPort(self, result):
        print(f'Port received from master {result}')
        self.port = result

    def switchConnectionToHub(self):
        point = TCP4ClientEndpoint(reactor, "localhost", self.port)
        self.deferred = connectProtocol(point, amp.AMP())
        self.deferred.addCallback(self.handshakeHub)
        self.deferred.addCallback(self.receiveID)
        self.deferred.addCallback(self.applyID)

    def handshakeHub(self, ampProto):
        print('Handshaking hub')
        return ampProto.callRemote(handshake.HandshakeHandler, asked=True)

    def receiveID(self, result):
        return result['id']

    def applyID(self, result):
        id = result.decode()
        print(f'Given ID {id}')
        self.givenID = id
        #reactor.stop()





