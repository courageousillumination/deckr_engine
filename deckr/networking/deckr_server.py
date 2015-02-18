"""
This module contains the code for running the deckr server.
"""

import json
import logging

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

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

    def inner(self, payload):  # pylint: disable=missing-docstring
        if self.game is None:
            self.send_error("You aren't connected to a game")
            return
        return func(self, payload)
    return inner


def requires_authenticated(func):
    """
    Can be put on a handler to indicate that it must be authenticated (mainly
    used for managment commands).
    """

    def inner(self, payload):
        if not self.authenticated:
            self.send_error("You aren't authenticated")
            return
        return func(self, payload)
    return inner


class DeckrProtocol(LineReceiver):

    """
    A simple protocol for the Deckr server.
    """

    def __init__(self, factory):
        self.factory = factory
        self.game = None
        self.authenticated = False
        self.player = None
        self.game_master = factory.game_master

    def send(self, message_type, data):
        """
        Send a message of the given message_type.
        """

        payload = {key: value for key, value in data.items()}
        payload['message_type'] = message_type
        self.transport.write(json.dumps(payload) + '\r\n')

    def broadcast_to_room(self, message_type, data):
        """
        Broadcast a message to the room (assumes the room exists)
        """
        payload = {key: value for key, value in data.items()}
        payload['message_type'] = message_type
        payload = json.dumps(payload) + '\r\n'
        for connection in self.factory.game_rooms[self.game.master_game_id]:
            connection.transport.write(payload)

    def send_error(self, message):
        """
        Send an error with the given message.
        """

        self.send('error', {'message': message})

    def lineReceived(self, data):
        """
        Process a single message. Mostly passes off to handler functions.
        """

        logging.debug("Recived a message %s", data)

        try:
            payload = json.loads(data)
        except ValueError:
            self.send_error("Malformed message: Could not decode JSON")
            return

        if 'message_type' not in payload:
            self.send_error("Malformed message: missing message_type")
            return

        message_type = payload['message_type']
        try:
            func = getattr(self, 'handle_' + message_type)
        except AttributeError:
            self.send_error(
                "Invalid message type: %s" %
                payload['message_type'])
            return
        func(payload) # Run the actual command

    # Server managment commands

    @requires_arguments(['secret_key'])
    def handle_authenticate(self, payload):
        """
        Handle the authenticate command.
        """

        print self.factory
        if payload['secret_key'] == self.factory.secret_key:
            self.authenticated = True
            self.send('authenticated', {})
        else:
            self.send_error("Invalid secret key")

    @requires_authenticated
    @requires_arguments(["game_definition_path"])
    def handle_register_game(self, payload):
        """
        Handle the register command.
        """

        def_id = self.game_master.register(payload['game_definition_path'])
        logging.info("Registering a new game located at %s",
                     payload['game_definition_path'])
        self.send('register_game_response', {'game_definition_id': def_id})

    # Game managment commands
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
        self.send('create_response',
                  {'game_id': game_id,
                   'game_type_id': payload['game_type_id']})

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
            if payload['player_id'] is None:
                self.player = game.add_player()
            else:
                self.player = game.get_object(payload['player_id'])
            player_id = self.player.game_id
        else:
            player_id = None

        # Everything is ok, actually connect to the game and send a response.
        self.game = game
        self.factory.game_rooms.setdefault(payload['game_id'], []).append(self)
        self.send('join_response', {'player_id': player_id})

    @requires_join
    def handle_quit(self, _):
        """
        Handle the quit command.
        """

        self.factory.game_rooms[self.game.master_game_id].remove(self)
        if self.factory.game_rooms[self.game.master_game_id] == []:
            del self.factory.game_rooms[self.game.master_game_id]
        self.game = None
        self.send('quit_response', {})

    @requires_join
    def handle_game_state(self, _):
        """
        Handle the game_state command.
        """

        self.send('game_state_response',
                  {'game_state': self.game.get_state(self.player)})

    @requires_join
    def handle_start(self, _):
        """
        Handle the start command. Should notify the room that the game has
        started.
        """

        self.game.set_up()
        self.broadcast_to_room('start', {})


class DeckrFactory(Factory):

    """
    The persistent backend for Deckr.
    """

    def __init__(self, config):
        self.game_master = GameMaster()
        self.game_rooms = {}
        self.secret_key = None

        for game in config['games']:
            self.game_master.register(game)

    def buildProtocol(self, addr):
        """
        Build the protocol.
        """

        return DeckrProtocol(self)
