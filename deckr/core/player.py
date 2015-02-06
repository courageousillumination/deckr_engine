"""
This file provides a simple interface for players.
"""

from deckr.core.game_object import GameObject
from deckr.core.zone import HasZones


class Player(GameObject, HasZones):

    """
    A simple stand in for player objects.
    """

    game_object_type = 'Player'

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
