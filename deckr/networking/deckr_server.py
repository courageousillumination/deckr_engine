"""
This module contains the code for running the deckr server.
"""

import json

from twisted.internet.protocol import Factory, Protocol

from deckr.core.game_master import GameMaster


def requires_arguments(arguments):
    """
    A simple decorator for DeckrProtocol handlers to specify which arguments
    are required. If any of the arguments are missing, sends an error and
    returns. Otherwise, runs and returns the function.
    """

    # pylint: disable=missing-docstring
    def wrapper(func):
        def inner(self, payload):
            for argument in arguments:
                if argument not in payload:
                    self.send_error("Missing required argument: %s" % argument)
                    return
            return func(self, payload)
        return inner
    return wrapper

def requires_join(func):
    """
    Can be put on a handler to indicate that it must be joined to a game before
    running.
    """

    def inner(self, payload):
        if self.game is None:
            self.send_error("You aren't connected to a game")
            return
        return func(self, payload)
    return inner


class DeckrProtocol(Protocol):

    """
    A simple protocol for the Deckr server.
    """

    def __init__(self, factory):
        self.factory = factory
        self.game = None
        self.game_master = factory.game_master

    def send(self, message_type, data):
        """
        Send a message of the given message_type.
        """

        payload = {key: value for key, value in data.items()}
        payload['message_type'] = message_type
        self.transport.write(json.dumps(payload) + '\r\n')

    def send_error(self, message):
        """
        Send an error with the given message.
        """

        self.send('error', {'message': message})

    def dataReceived(self, data):
        """
        Process a single message. Mostly passes off to handler functions.
        """

        try:
            payload = json.loads(data)
        except ValueError:
            self.send_error("Malformed message: Could not decode JSON")

        if 'message_type' not in payload:
            self.send_error("Malformed message: missing message_type")

        message_type = payload['message_type']
        try:
            getattr(self, 'handle_' + message_type)(payload)
        except AttributeError:
            self.send_error("Invalid message type: %s" % payload['message_type'])

    def handle_list(self, _):
        """
        Handle a list command. Mainly returns the list from the game_master.
        """

        self.send('list_response',
                  {'game_types': self.game_master.list_game_types()})

    @requires_arguments(['game_type_id'])
    def handle_create(self, payload):
        """
        Handle the create command.
        """

        try:
            game_id = self.game_master.create(payload['game_type_id'])
        except KeyError:
            self.send_error(
                "No game type with id %s" %
                payload['game_type_id'])
            return
        self.send('create_response', {'game_id': game_id})

    @requires_arguments(['game_id'])
    def handle_destroy(self, payload):
        """
        Handle the destroy command.
        """

        try:
            self.game_master.destroy(payload['game_id'])
        except KeyError:
            self.send_error("No game with id %s" % payload['game_id'])
            return
        self.send('destroy_response', {'game_id': payload['game_id']})

    @requires_arguments(['game_id'])
    def handle_join(self, payload):
        """
        Handle the join command.
        """

        # Make sure we're not already connected to a game
        if self.game is not None:
            self.send_error("You are already connected to game")
            return

        # Get the game
        try:
            game = self.game_master.get_game(payload['game_id'])
        except KeyError:
            self.send_error("No game with id %s" % payload['game_id'])
            return

        # Either add a player or join as spectator
        if 'player_id' in payload:
            player_id = 1
        else:
            player_id = None

        # Everything is ok, actually connect to the game and send a response.
        self.game = game
        self.send('join_response', {'player_id': player_id})

    @requires_join
    def handle_quit(self, payload):
        """
        Handle the quit command.
        """

        self.game = None
        self.send('quit_response', {})


class DeckrFactory(Factory):

    """
    The persistent backend for Deckr.
    """

    def __init__(self):
        self.game_master = GameMaster()

    def buildProtocol(self, addr):
        """
        Build the protocol.
        """

        return DeckrProtocol(self)
