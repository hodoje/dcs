from threading import Thread, Lock


class Emitter:
    def __init__(self, factory):
        self._factory = factory

    def startEmitting(self):
        connections = self._factory.getConnections()
        for client in connections:
            lock = Lock()
            thread = Thread(target=self.emitData, args=[client, self._factory.dataBuffer, lock])
            thread.start()

    def emitData(self, client, dataBuffer, lock):
        if dataBuffer:
            lock.aquire(True)
            data = dataBuffer.pop(0)
            lock.release()
            client.transport.write(data)