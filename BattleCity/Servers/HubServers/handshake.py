from twisted.internet.protocol import Factory
from twisted.protocols import amp
from twisted.internet import reactor

class HandshakeHandler(amp.Command):
    arguments = []

    response = [(b'id', amp.String())]

    errors = {ConnectionError: b'Could not send'}


class HandshakeProtocol(amp.AMP):
    def __init__(self, factory):
        self._factory = factory
        super(HandshakeProtocol, self).__init__()

    def ReceiveGameRequest(self):
        return {'id': self.factory.generatePlayerId()}


class HandshakeFactory(Factory):
    def __init__(self):
        self.playerID = 'ID#'
        self.playerID_iterator = 0

    def buildProtocol(self, addr):
        return HandshakeProtocol(self)

    def generatePlayerId(self):
        self.playerIDIterator += 1
        return self.playerID + str(self.playerIDIterator)

def main(port):
    pf = HandshakeFactory()
    reactor.listenTCP(port, pf)
    print('Started handshake with client')
