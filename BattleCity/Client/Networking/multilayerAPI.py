from twisted.internet import reactor


from Client.Networking.initiateMPRequest import GameRequest


if __name__ == '__main__':
    gameRequest = GameRequest()
    print('Input game mode:')
    gameRequest.initiate(int(input()))
    reactor.run()