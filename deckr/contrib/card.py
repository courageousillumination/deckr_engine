"""
This module provides a common interface for cards. These can be used in basic
card games and other things.
"""

from deckr.core.game_object import GameObject


class Card(GameObject):

    """
    This represents a generic card in any card game.
    """

    game_object_type = 'Card'

    def __init__(self, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)

        self.set_game_attribute('face_up', False)
