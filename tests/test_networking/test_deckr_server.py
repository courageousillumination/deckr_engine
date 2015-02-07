"""
Tests around the DeckrServer.
"""

import json
from unittest import TestCase

from twisted.test import proto_helpers

from deckr.networking.deckr_server import DeckrFactory
from tests.settings import SIMPLE_GAME


class DeckrServerTestCase(TestCase):

    """
    The base class for the deckrserver test cases. Builds a game master with
    a single game and creates the server connected to that game master.
    """

    def setUp(self):
        self.factory = DeckrFactory({'games': [SIMPLE_GAME]})
        # Set up the game master
        self.game_master = self.factory.game_master
        self.simple_game_id = self.game_master.game_type_id - 1 # TODO: Fix.
        # Set up the server with a string transport
        self.protocol = self.factory.buildProtocol(('127.0.0.1', 0))
        self.transport = proto_helpers.StringTransport()
        self.protocol.makeConnection(self.transport)

    def run_command(self, message_type, protocol=None, **kwargs):
        """
        A utility function to run commands with specified parameters.
        """
        kwargs['message_type'] = message_type
        payload = json.dumps(kwargs)
        if protocol is None:
            self.protocol.lineReceived(payload)
        else:
            protocol.lineReceived(payload)

    def get_response(self, expected_message_type=None, transport=None):
        """
        Get a decoded response out of the string transport. Returns the decoded
        dictonary.
        """

        if transport is None:
            transport = self.transport
        value = transport.value()
        print value
        try:
            data = json.loads(value)
        except ValueError:
            self.fail()
        if expected_message_type is not None:
            self.assertEqual(expected_message_type, data['message_type'])
        transport.clear()
        return data

    def assert_produces_error(self, expected_error_message=None):
        """
        Assert that some code produces an error message.
        """

        error = self.get_response('error')
        self.assertEqual(error['message'], expected_error_message)

class DeckrServerManagmentTestCase(DeckrServerTestCase):
    """
    Test the server managment commands.
    """

    def seUp(self):
        super(DeckrServerManagmentTestCase, self).setUp()


    def test_register_game(self):
        """
        Make sure we can register a game properly.
        """

        self.factory.secret_key = 'foobar'
        self.run_command('authenticate', secret_key='foobar')
        self.get_response('authenticated')

        self.run_command('register_game', game_definition_path=SIMPLE_GAME)
        response = self.get_response('register_game_response')
        self.assertIsNotNone(response['game_definition_id'])

        self.run_command('list')
        game_types = self.get_response('list_response')['game_types']
        self.assertEqual(len(game_types), 2)

class DeckrServerGameTestCase(DeckrServerTestCase):

    """
    Test commands specifically related to games.
    """

    def setUp(self):
        super(DeckrServerGameTestCase, self).setUp()
        self.run_command('create', game_type_id=self.simple_game_id)
        self.game_id = self.get_response('create_response')['game_id']

    def test_join(self):
        """
        Test the join command. This takes a game id that should be joined.
        """

        self.run_command('join')
        self.assert_produces_error("Missing required argument: game_id")

        self.run_command('join', game_id=-1)
        self.assert_produces_error("No game with id -1")

        # Join as spectator
        self.run_command('join', game_id=self.game_id)
        response = self.get_response('join_response')
        self.assertEqual(response['player_id'], None)

        # You can't join a game if you've already connected to a game.
        self.run_command('join', game_id=self.game_id)
        self.assert_produces_error("You are already connected to game")

        self.run_command('quit')
        self.get_response()

        # Join as a new player
        self.run_command('join', game_id=self.game_id, player_id=None)
        response = self.get_response('join_response')
        self.assertIsNotNone(response['player_id'])
        player_id = response['player_id']

        self.run_command('quit')
        self.get_response()

        # Join as an existing player
        self.run_command('join', game_id=self.game_id, player_id=player_id)
        response = self.get_response('join_response')
        self.assertEqual(response['player_id'], player_id)

    def test_quit(self):
        """
        Test the quit command.
        """

        self.run_command('quit')
        self.assert_produces_error("You aren't connected to a game")

        # Make sure we actually get a quit response
        self.run_command('join', game_id=self.game_id)
        self.get_response()
        self.run_command('quit')
        self.get_response('quit_response')

    def test_request_game_state(self):
        """
        Test the request game state function.
        """

        self.run_command('join', game_id=self.game_id)
        self.get_response()

        self.run_command('game_state')
        response = self.get_response('game_state_response')
        self.assertIn('game_state', response)

    def test_start(self):
        """
        Test the start command.
        """

        # Build another protocl
        other_protocol = self.factory.buildProtocol(('127.0.0.1', 0))
        other_transport = proto_helpers.StringTransport()
        other_protocol.makeConnection(other_transport)

        # Join with both
        self.run_command('join', game_id=self.game_id)
        self.run_command('join', game_id=self.game_id, protocol=other_protocol)
        self.get_response()
        self.get_response(transport=other_transport)

        self.run_command('start')
        # We expect both to get a start message.
        self.get_response('start')
        self.get_response('start', transport=other_transport)


class DeckrServerGameManagmentTestCase(DeckrServerTestCase):

    """
    Contains tests for the deckr server game managment commands. These commands
    are list, create, and destroy.
    """

    def test_list(self):
        """
        Test the list command. This can be run at any point and should return
        a list of all games supported by the server.
        """

        self.run_command('list')
        self.assertEqual(self.get_response('list_response')['game_types'],
                         [[self.simple_game_id, 'Simple Game']])

    def test_create(self):
        """
        Test the create command. This can be run at any time, and requires
        one argument (game_type_id).
        """

        self.run_command('create', game_type_id=self.simple_game_id)
        response = self.get_response('create_response')
        self.assertIn('game_id', response)

        # Test the error conditions
        self.run_command('create', game_type_id=-1)
        self.assert_produces_error("No game type with id -1")

        self.run_command('create')
        self.assert_produces_error("Missing required argument: game_type_id")

    def test_destroy(self):
        """
        Test the destroy command. This can be run at any time and requires
        exactly one argument (game_id).
        """

        # Create a game
        self.run_command('create', game_type_id=self.simple_game_id)
        game_id = self.get_response('create_response')['game_id']

        self.run_command('destroy', game_id=game_id)
        self.get_response('destroy_response')

        # Test the edge conditions
        self.run_command('destroy', game_id=game_id)
        self.assert_produces_error("No game with id %s" % game_id)

        self.run_command('destroy')
        self.assert_produces_error("Missing required argument: game_id")

    def test_malformed_messages(self):
        """
        Make sure that we can properly handle several different types of
        malformed message.
        """

        self.run_command('foobar')
        self.assert_produces_error("Invalid message type: foobar")

        # Send something that isn't even json.
        self.protocol.lineReceived("foobar")
        self.assert_produces_error("Malformed message: Could not decode JSON")

        # Send something that is json but without a message type
        self.protocol.lineReceived('{"foo": "bar"}')
        self.assert_produces_error("Malformed message: missing message_type")
