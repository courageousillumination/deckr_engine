"""
This file contains all of the tests cases around the base game.
"""

from unittest import TestCase

from deckr.core.exceptions import FailedRestrictionException, TooManyPlayers
from deckr.core.game import action, Game, restriction
from deckr.core.game_object import GameObject
from deckr.core.player import Player


class GameTestCase(TestCase):

    """
    This module contains all tests around the core game. The main functionality
    tested here includes:
        * Object registration
        * Making actions
        * Creating updates
    """

    def setUp(self):
        self.game = Game()

    def test_object_registration(self):
        """
        Make sure that we can register, lookup, and deregister game objects.
        """

        game_object = GameObject()
        game_id = self.game.register(game_object)

        self.assertEqual(game_object.game_id, game_id)
        self.assertEqual(self.game.get_object(game_id), game_object)

        self.game.deregister(game_object)

        self.assertIsNone(game_object.game_id)
        self.assertIsNone(self.game.get_object(game_id))

        # Test registration/dergistration with a list
        game_ids = self.game.register([game_object])

        self.assertEqual(len(game_ids), 1)
        self.assertEqual(game_ids[0], game_object.game_id)
        self.assertEqual(self.game.get_object(game_ids[0]), game_object)

        self.game.deregister([game_object])

        self.assertIsNone(game_object.game_id)
        self.assertIsNone(self.game.get_object(game_ids[0]))

        # Test corner cases: double register, double deregister, lookup with bad
        # id.
        game_id = self.game.register(game_object)
        game_id1 = self.game.register(game_object)

        self.assertEqual(game_id, game_id1)

        self.assertRaises(ValueError, self.game.get_object, game_id, int)

        self.game.deregister(game_object)
        self.game.deregister(game_object)

    def test_get_state(self):
        """
        Make sure that we can get the state out of the game at any point.
        """

        game_object1 = GameObject()
        game_object2 = GameObject()

        result = self.game.register([game_object1, game_object2])
        id1 = result[0]
        id2 = result[1]

        expected = {}
        expected[0] = {'game_id': 0, 'type': 'Game'}
        expected[id1] = {'game_id': id1, 'type': 'GameObject'}
        expected[id2] = {'game_id': id2, 'type': 'GameObject'}

        result = {x['game_id']: x for x in self.game.get_state()}
        self.assertDictEqual(result, expected)

        # Test setting an extra attribute
        game_object1.set_game_attribute('foo', 'bar')
        expected[id1]['foo'] = 'bar'

        result = {x['game_id']: x for x in self.game.get_state()}
        self.assertDictEqual(result, expected)

    def test_action(self):
        """
        Test actions, especially regarding restrictions.
        """

        # pylint: disable=unused-argument,missing-docstring
        @restriction('Must start with foo')
        def restriction1(input_string, **kwargs):
            return input_string.startswith('foo')

        @restriction('Must end with bar')
        def restriction2(input_string, **kwargs):
            return input_string.endswith('bar')

        @action(restrictions=(restriction1, restriction2))
        def simple_action(input_string):
            return input_string + ' magic'

        @action()
        def unrestricted():
            return 'foo'

        self.assertRaises(FailedRestrictionException, simple_action,
                          input_string='hello')
        self.assertRaises(FailedRestrictionException, simple_action,
                          input_string='foo')
        self.assertEqual(simple_action('foo bar'), 'foo bar magic')
        self.assertEqual(unrestricted(), 'foo')

    def test_game_zones(self):
        """
        Test that the game can load its zones and player zones properly.
        """

        class TestGame(Game):

            """
            A simple game with game zones and player zones.
            """

            game_zones = [{'name': 'simple_zone'}]
            player_zones = [{'name': 'player_zone'}]

            def __init__(self, *args, **kwargs):
                super(TestGame, self).__init__(*args, **kwargs)

            def set_up(self):
                """
                no-op.
                """

                pass

        game = TestGame()
        self.assertTrue(hasattr(game, 'simple_zone'))

        player = game.add_player()
        self.assertTrue(hasattr(player, 'player_zone'))

    def test_add_player(self):
        """
        Make sure that we can properly add a player.
        """

        player = self.game.add_player()
        self.assertTrue(isinstance(player, Player))
        self.assertEqual(len(self.game.players), 1)

        self.game.max_players = 1
        self.assertRaises(TooManyPlayers, self.game.add_player)

    def test_transitions(self):
        """
        Make sure we can properly register transitions, get them for individual
        players, etc.
        """

        player1 = self.game.add_player()
        player2 = self.game.add_player()

        self.game.add_transition({'foo': 'bar'})  # Add for all players
        result = self.game.get_all_transitions()
        self.assertEqual(result, [(player1, [{'foo': 'bar'}]),
                                  (player2, [{'foo': 'bar'}])])

        self.game.add_transition({'baz': 'foo'}, player1)
        result = self.game.get_all_transitions()
        self.assertEqual(result, [(player1, [{'foo': 'bar'}, {'baz': 'foo'}]),
                                  (player2, [{'foo': 'bar'}])])

        self.game.flush_all_transitions()
        self.assertEqual(self.game.get_all_transitions(),
                         [(player1, []), (player2, [])])
