from unittest import TestCase

from client import Client
from deckr.networking.game_server import GameServer
from nose.plugins.attrib import attr


@attr('networking')
class GameServerTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.server = GameServer()
