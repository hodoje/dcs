from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol
from twisted.protocols import amp
from twisted.internet import reactor

from Servers.MasterServer import master


class GameRequest:
    def __init__(self, port=8999):
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

    def handshakeMaster(self, ampProto):
        print('Handshakeing master')
        gameMode = self.gameMode
        return ampProto.callRemote(master.ReceiveGameRequestHandler, gameMode=gameMode)

    def recieveHubsPort(self, result):
        return result['hubPort']

    def applyNewPort(self, result):
        print(f'Port received from master {result}')
        self.port = result




