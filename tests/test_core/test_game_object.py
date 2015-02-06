"""
This file provides all tests around basic game objects.
"""

from unittest import TestCase

from deckr.core.game import Game
from deckr.core.game_object import GameObject
from deckr.core.player import Player


class GameObjectTestCase(TestCase):

    """
    This testcase is mainly around all the code related to game objects.
    """

    def setUp(self):
        self.game = Game()
        self.game_object = GameObject()
        self.player1 = Player()
        self.player2 = Player()
        self.game.register([self.game_object, self.player1, self.player2])

    def test_serialize(self):
        """
        Make sure that we can serialize a game object into a dictionary.
        """

        result = self.game_object.serialize()
        self.assertDictEqual(result, {'game_id': self.game_object.game_id,
                                      'type': 'GameObject'})

    def test_game_attribute(self):
        """
        Make sure that we can interact with game attributes.
        """

        self.game_object.set_game_attribute('foo', 'bar')
        self.assertEqual(self.game_object.get_game_attribute('foo'), 'bar')

        # Test per player attribute overrides
        self.game_object.set_game_attribute('foo', 'baz', player=self.player1)

        self.assertEqual(self.game_object.get_game_attribute('foo'), 'bar')
        result = self.game_object.get_game_attribute(
            'foo',
            player=self.player1)
        self.assertEqual(result, 'baz')
        result = self.game_object.get_game_attribute(
            'foo',
            player=self.player2)
        self.assertEqual(result, 'bar')

        # Test error conditions
        self.assertRaises(AttributeError, self.game_object.get_game_attribute,
                          'bar')
