from twisted.internet.protocol import Factory
from twisted.protocols import amp
from twisted.internet import reactor


class HandshakeHandler(amp.Command):
    arguments = [(b'asked', amp.Boolean())]

    response = [(b'id', amp.String())]

    errors = {ConnectionError: b'Could not send'}


class HandshakeProtocol(amp.AMP):
    def __init__(self, factory):
        self._factory = factory
        super(HandshakeProtocol, self).__init__()

    @HandshakeHandler.responder
    def ReceiveGameRequest(self, asked):
        if asked:
            id = self._factory.generatePlayerId().encode()
            return {'id': id}
        return


class HandshakeFactory(Factory):

    def buildProtocol(self, addr):
        return HandshakeProtocol(self)


#def main(port):
    #pf = HandshakeFactory()
    #reactor.listenTCP(port, pf)
    #print('Started handshake with client')
