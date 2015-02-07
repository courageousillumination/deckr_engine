"""
This file contains code for the game master.
"""

import logging

from deckr.core.game_definition import GameDefinition


class GameMaster(object):

    """
    The GameMaster provides game managment and a central point for all deckr
    games. This class offers a list of games that it supports, and interfaces
    to create and destory games. It will store a dictionary of all games that
    this master manages.
    """

    def __init__(self):
        self.game_types = {}
        self.games = {}
        self.game_type_id = 0
        self.game_id = 0

    def register(self, game_path):
        """
        Register a game with this game master.
        """

        logging.info("Registering game %s", game_path)
        game_definition = GameDefinition()
        game_definition.load(game_path)
        self.game_types[self.game_type_id] = game_definition
        self.game_type_id += 1
        return self.game_type_id - 1

    def create(self, game_type_id):
        """
        Create a new game instance, of the specified game type. Returns
        the game id of the newly created game.
        """

        game = self.game_types[game_type_id].create_instance()
        self.games[self.game_id] = game
        game.game_id = self.game_id
        self.game_id += 1
        return game.game_id

    def destroy(self, game_id):
        """
        Destroy the game with the given ID. Calls appropriate clean up function
        on the game.
        """

        del self.games[game_id]

    def list_game_types(self):
        """
        List all the game types.
        """

        return [(key, self.game_types[key].name) for key in self.game_types]

    def get_game(self, game_id):
        """
        Get the game for a specific id.
        """

        return self.games[game_id]
