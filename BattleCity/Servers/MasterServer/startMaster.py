from Servers.MasterServer.master import MasterFactory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

if __name__ == '__main__':
    mf = MasterFactory()
    endpoint = TCP4ServerEndpoint(reactor, mf.port)
    endpoint.listen(mf)
    print('ready to receive')
    reactor.run()
