"""
This file provides all the code related to zones.
"""

import copy

from deckr.core.game_object import GameObject


class Zone(GameObject):

    """
    A zone acts very similarly to a list, but it includes builtin functionality
    for handling game objects.
    """

    game_object_type = 'Zone'

    def __init__(self, *args, **kwargs):
        super(Zone, self).__init__(*args, **kwargs)
        self._zone = []

    def push(self, obj):
        """
        Push a game object into this zone.
        """

        self._zone.append(obj)
        if self.game is not None:
            self.game.add_transition({'transition_type': 'add',
                                      'target_zone': self.game_id,
                                      'object': obj.game_id})

    def pop(self):
        """
        Returns the last object that was pushed into the zone. None if no
        such element exists.
        """

        try:
            obj = self._zone.pop()
        except IndexError:
            return None

        if self.game is not None:
            self.game.add_transition({'transition_type': 'remove',
                                      'target_zone': self.game_id,
                                      'object': obj.game_id})
        return obj

    def add(self, obj):
        """
        Add an object to the zone without any guarntees about order.
        """

        self.push(obj)

    def remove(self, obj):
        """
        Remove a specificed object from the zone.
        """

        try:
            self._zone.remove(obj)
        except ValueError:
            return

        if self.game is not None:
            self.game.add_transition({'transition_type': 'remove',
                                      'target_zone': self.game_id,
                                      'object': obj.game_id})

    def set(self, objs):
        """
        Takes in a list and sets the current inner zone to that list.
        """

        self.clear()
        for obj in objs:
            self.push(obj)

    def clear(self):
        """
        Completely clear out everything in this zone.
        """

        while len(self._zone) != 0:
            self._zone.pop()

    def transfer(self, target_zone):
        """
        Send all of the objects in this zone to another zone.
        """

        target_zone.set(self._zone)
        self.clear()

    def serialize(self, player=None):
        """
        This will include an 'objects' element in the serialized result that
        contains a list of all the game_ids.
        """

        result = super(Zone, self).serialize(player)
        result['objects'] = [x.game_id for x in self._zone]
        return result

    # Builtins
    def __iter__(self):
        """
        Provide an iterator for the zone.
        """

        for obj in self._zone:
            yield obj

    def __contains__(self, obj):
        """
        Check for containment in the zone.
        """

        return obj in self._zone

    def __getitem__(self, index):
        """
        Get an item at the specified index.
        """

        return self._zone[index]

    def __len__(self):
        """
        Proxy to the underlying _zone object.
        """

        return len(self._zone)


class HasZones(object):

    """
    This is a mixin that can be thrown on players, games, etc. It provides
    functionality for loading dictionaries into zones on the object.
    """

    def __init__(self, *args, **kwargs):
        super(HasZones, self).__init__(*args, **kwargs)
        self.zones = {}

    def load_zones(self, zone_list):
        """
        Loads up a list of zones. The argument should be a list of dictionaries.
        Each dictionary should have at the very least a name. If 'multiplicity'
        is included in the dictionary it will create multiple instances of the
        zone. These will be named ZONE_NAME0, ZONE_NAME1, ...,
        ZONE_NAME(multiplicity).
        """

        for zone_config in zone_list:
            zone_config = copy.copy(zone_config)
            zone_name = zone_config.pop('name')
            if 'multiplicity' in zone_config:
                count = zone_config.pop('multiplicity')
                for i in range(count):
                    self._add_zone(zone_config, zone_name + str(i))
            else:
                self._add_zone(zone_config, zone_name)

    def _add_zone(self, zone_config, zone_name):
        """
        Adds a single zone with the specified name and configuration.
        """

        zone = Zone()
        zone.set_game_attribute('name', zone_name)
        setattr(self, zone_name, zone)
        for key, value in zone_config.items():
            setattr(zone, key, value)
        self.zones[zone_name] = zone
        self.post_add_zone_callback(zone)

    def post_add_zone_callback(self, zone):
        """
        This can be overriden by subclasses to implement extra code after
        adding a zone.
        """

        pass
