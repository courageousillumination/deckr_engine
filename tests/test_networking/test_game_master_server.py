from unittest import TestCase

from client import Client
from deckr.networking.game_master_server import GameMasterServer
from nose.plugins.attrib import attr
from tests.settings import SAMPLE_GAME


@attr('networking')
class GameMasterServerTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.server = GameMasterServer()
        # Configure the server
        self.server.register_game(SAMPLE_GAME)

    def test_list(self):
        self.client.send_command('list')
        response = self.client.wait_for_response()

        self.assertEqual(response['message_type'], 'game_types')
        game_types = response['arguments']['games']
        self.assertEqual(len(game_types), 1)
