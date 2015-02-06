"""
This file provides all tests around basic game definitions.
"""

from unittest import TestCase

from deckr.core.game import Game
from deckr.core.game_definition import GameDefinition
from tests.settings import BAD_GAME, SIMPLE_GAME


class GameDefinitionTestCase(TestCase):

    """
    This testcase is mainly around all the code related to game definitions
    """

    def setUp(self):
        self.game_definition = GameDefinition()

    def test_load(self):
        """
        Make sure we can load up a game definition from a path.
        """

        self.game_definition.load(SIMPLE_GAME)
        self.assertTrue(issubclass(self.game_definition.klass, Game))
        self.assertEqual(self.game_definition.name, "Simple Game")

    def test_fail_load(self):
        """
        Make sure we can properly handle failed loads.
        """

        self.assertRaises(ValueError, self.game_definition.load, BAD_GAME)

    def test_create_instance(self):
        """
        Make sure we can create an instance.
        """

        self.game_definition.load(SIMPLE_GAME)
        self.assertTrue(isinstance(self.game_definition.create_instance(),
                                   Game))
