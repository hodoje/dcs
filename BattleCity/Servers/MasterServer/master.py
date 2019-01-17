from twisted.internet.protocol import Factory
from twisted.protocols import amp
from twisted.internet import error

from multiprocessing import Process, Pipe

from Servers.HubServers import handleClients


class ReceiveGameRequestHandler(amp.Command):
    arguments = [(b'gameMode', amp.Integer())]

    response = [(b'hubPort', amp.Integer())]

    errors = {ConnectionRefusedError: b'ConnectionNotEstablished'}


class MasterProtocol(amp.AMP):
    def __init__(self, factory):
        self._factory = factory
        super(MasterProtocol, self).__init__()

    def connectionMade(self):
        _peer = self.transport.getPeer()
        print(f'Conection made with client {_peer.host}:{_peer.port}')
        return

    def connectionLost(self, reason=error.ConnectionDone):
        if reason.check(error.ConnectionDone):
            print(reason.getErrorMessage())
        else:
            print("Connection violently broke: {}".format(reason.getErrorMessage))

    @ReceiveGameRequestHandler.responder
    def receiveGameRequest(self, gameMode):
        hubPort = self._factory.getPort()

        if len(self._factory.hubFactories) == 0:
            self._factory.addHub(self.createNewHub(hubPort, gameMode))

        # Check for open slots, else create a new hub
        for pf in self._factory.hubFactories:
            if pf.checkGameMode(gameMode):
                hubPort = pf.hubsPort
                return {'hubPort': hubPort}

        self._factory.append(self.createNewHub(hubPort, gameMode))
        return {'hubPort': hubPort}

    # instantiate new hub, run as new proces, communicate via pipe
    def createNewHub(self, port, gameMode):
        masterPipePoint, hubPipePoint = Pipe()
        hub = Process(target=handleClients.handleConnection, args=(port, gameMode, hubPipePoint))
        hub.start()
        hubFactory = masterPipePoint.recv() # recv hub factory
        self._factory.pipeEndpoints.append(masterPipePoint)
        return hubFactory


class MasterFactory(Factory):
    def __init__(self):
        self.port = 8999
        self.hubPort = 10010
        self.hubFactories = []
        self.pipeEndpoints = []

    def buildProtocol(self, addr):
        return MasterProtocol(self)

    def addHub(self, factory):
        self.hubFactories.append(factory)

    def getPort(self):
        self.hubPort += 1
        return self.hubPort
