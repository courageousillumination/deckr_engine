import json

from twisted.internet.protocol import Factory, Protocol

from deckr.core.game_master import GameMaster


class DeckrProtocol(Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.game_master = factory.game_master

    def send(self, message_type, data):
        payload = {key: value for key, value in data.items()}
        payload['message_type'] = message_type
        self.transport.write(json.dumps(payload) + '\r\n')

    def send_error(self, message):
        self.send('error', {'message': message})

    def dataReceived(self, data):
        try:
            payload = json.loads(data)
        except ValueError:
            self.send_error("Malformed message: Could not decode JSON")

        if 'message_type' not in payload:
            self.send_error("Malformed message: missing message_type")

        message_type = payload['message_type']
        if message_type == 'create':
            self.handle_create(payload)
        elif message_type == 'list':
            self.handle_list(payload)
        elif message_type == 'destroy':
            self.handle_destroy(payload)

    def handle_create(self, payload):
        try:
            game_id = self.game_master.create(payload['game_type_id'])
        except KeyError:
            self.send_error("No game type with id %s" % payload['game_type_id'])
            return
        self.send('create_response', {'game_id': game_id})

    def handle_list(self, payload):
        self.send('list_response', {'game_types': self.game_master.list_game_types()})

    def handle_destroy(self, payload):
        self.send('destroy_response', {'game_id': payload['game_id']})

class DeckrFactory(Factory):

    def __init__(self):
        self.game_master = GameMaster()

    def buildProtocol(self, addr):
        return DeckrProtocol(self)
