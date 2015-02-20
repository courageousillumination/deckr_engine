"""
This file contains all the tests around zones.
"""

from unittest import TestCase

from deckr.core.game import Game
from deckr.core.game_object import GameObject
from deckr.core.zone import HasZones, Zone


class HasZonesTestCase(TestCase):

    """
    Test the HasZones mixin.
    """

    def setUp(self):
        self.has_zones = HasZones()

    def test_load_zones(self):
        """
        Make sure that we can load all of the zones with different
        configurations.
        """

        # pylint: disable=protected-access

        # Vanilla zone
        self.has_zones.load_zones([{'name': 'sample_zone'}])
        self.assertTrue(hasattr(self.has_zones, 'sample_zone'))
        self.assertTrue(isinstance(self.has_zones.sample_zone, Zone))
        self.assertIn('sample_zone', self.has_zones.zones)

        # Zones with multiplicity
        self.has_zones.load_zones([{'name': 'multiple_zones',
                                    'multiplicity': 5}])
        for i in range(5):
            name = 'multiple_zones' + str(i)
            self.assertTrue(hasattr(self.has_zones, name))
            self.assertIn(name, self.has_zones.zones)

        # Zones with additional attributes
        self.has_zones.load_zones([{'name': 'attribute_zone', 'foo': 'bar'}])
        self.assertTrue(hasattr(self.has_zones, 'attribute_zone'))
        self.assertEqual(self.has_zones.attribute_zone.foo, 'bar')
        zone_name = self.has_zones.attribute_zone.get_game_attribute('name')
        self.assertEqual(zone_name, 'attribute_zone')

    def test_load_zone_callback(self):
        """
        Make sure we properly call the callback.
        """

        # pylint: disable=missing-docstring
        class MockHasZones(HasZones):

            def __init__(self):
                super(MockHasZones, self).__init__()
                self.added_zone = None

            def post_add_zone_callback(self, zone):
                self.added_zone = zone

        has_zones = MockHasZones()
        has_zones.load_zones([{'name': 'sample_zone'}])
        self.assertTrue(isinstance(has_zones.added_zone, Zone))


class ZoneTestCase(TestCase):

    """
    Test the Zone class itself.
    """

    def setUp(self):
        self.zone = Zone()
        self.game_object1 = GameObject()
        self.game_object2 = GameObject()
        self.game_object3 = GameObject()

    def test_push_and_pop(self):
        """
        Test the basics of pushing and poping onto a zone.
        """

        self.zone.push(self.game_object1)
        self.zone.push(self.game_object2)
        self.zone.push(self.game_object3)

        self.assertEqual(self.game_object3, self.zone.pop())
        self.assertEqual(self.game_object2, self.zone.pop())
        self.assertEqual(self.game_object1, self.zone.pop())

        self.assertIsNone(self.zone.pop())

    def test_add_and_remove(self):
        """
        Test the basics of unorderd operations.
        """

        self.zone.add(self.game_object1)
        self.assertIn(self.game_object1, self.zone)

        self.zone.remove(self.game_object1)
        self.assertNotIn(self.game_object1, self.zone)
        self.zone.remove(self.game_object1)

    def test_set_clear_transfer(self):
        """
        Test the mass operations (putting a list, clearing, transfering).
        """

        self.zone.set(
            [self.game_object1, self.game_object2, self.game_object3])
        self.assertIn(self.game_object1, self.zone)
        self.assertIn(self.game_object2, self.zone)
        self.assertIn(self.game_object3, self.zone)

        self.zone.clear()
        self.assertNotIn(self.game_object1, self.zone)
        self.assertNotIn(self.game_object2, self.zone)
        self.assertNotIn(self.game_object3, self.zone)

        zone2 = Zone()
        zone2.set([self.game_object1, self.game_object2, self.game_object3])

        zone2.transfer(self.zone)
        self.assertIn(self.game_object1, self.zone)
        self.assertIn(self.game_object2, self.zone)
        self.assertIn(self.game_object3, self.zone)
        self.assertNotIn(self.game_object1, zone2)
        self.assertNotIn(self.game_object2, zone2)
        self.assertNotIn(self.game_object3, zone2)

    def test_builtins(self):
        """
        Test several builtins: len, slicing, indexing, in, iteration.
        """

        self.zone.push(self.game_object1)
        self.zone.push(self.game_object2)
        self.zone.push(self.game_object3)

        # Test the in operator
        self.assertIn(self.game_object1, self.zone)
        self.assertIn(self.game_object2, self.zone)
        self.assertIn(self.game_object3, self.zone)

        # Test slicing and indexing
        self.assertEqual(self.zone[-1], self.game_object3)
        self.assertEqual(self.zone[0:2],
                         [self.game_object1, self.game_object2])

        # Test iteration
        count = 0
        for obj in self.zone:
            count += 1
            all_objs = [
                self.game_object1,
                self.game_object2,
                self.game_object3]
            self.assertIn(obj, all_objs)
        self.assertEqual(count, 3)

        # Test len
        self.assertEqual(len(self.zone), 3)

    def test_serialize(self):
        """
        Make sure that we serialize properly.
        """

        self.zone.push(self.game_object1)
        self.zone.push(self.game_object2)
        self.zone.push(self.game_object3)
        # Fake game ids
        self.zone.game_id = 1
        self.game_object1.game_id = 2
        self.game_object2.game_id = 3
        self.game_object3.game_id = 4

        self.assertEqual(self.zone.serialize(),
                         {'game_id': 1, 'type': 'Zone', 'objects': [2, 3, 4]})

    def test_transitions(self):
        """
        Make sure that we can properly register transitions.
        """

        game = Game()
        game.register(
            [self.game_object1, self.game_object2, self.game_object3])
        game.register(self.zone)
        player = game.add_player()

        self.zone.push(self.game_object1)
        self.assertEqual(game.get_transitions(player),
                         [{'update_type': 'add',
                           'game_object': self.game_object1.game_id,
                           'zone': self.zone.game_id}])
        game.flush_all_transitions()

        self.zone.add(self.game_object1)
        self.assertEqual(game.get_transitions(player),
                         [{'update_type': 'add',
                           'game_object': self.game_object1.game_id,
                           'zone': self.zone.game_id}])
        game.flush_all_transitions()

        self.zone.set([self.game_object1])
        self.assertEqual(game.get_transitions(player),
                         [{'update_type': 'add',
                           'game_object': self.game_object1.game_id,
                           'zone': self.zone.game_id}])
        game.flush_all_transitions()

        self.zone.set(
            [self.game_object1, self.game_object2, self.game_object3])
        game.flush_all_transitions()
        obj = self.zone.pop()
        self.assertEqual(game.get_transitions(player),
                         [{'update_type': 'remove',
                           'game_object': obj.game_id,
                           'zone': self.zone.game_id}])
        game.flush_all_transitions()

        self.zone.remove(self.game_object2)
        self.assertEqual(game.get_transitions(player),
                         [{'update_type': 'remove',
                           'game_object': self.game_object2.game_id,
                           'zone': self.zone.game_id}])
