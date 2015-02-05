"""
This file contains code for the game master.
"""


class GameMaster(object):

    """
    The deckr game master.
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

        self.game_types[self.game_type_id] = game_path
        self.game_type_id += 1
        return self.game_type_id - 1

    def create(self, game_type_id):
        """
        Create a new game instance, of the specified game type. Returns
        the game id of the newly created game.
        """

        _ = self.game_types[game_type_id]
        self.games[self.game_id] = None
        self.game_id += 1
        return self.game_id - 1

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

        return self.game_types.items()
