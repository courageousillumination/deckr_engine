"""
This file provides the base Game class. Any game will have to extend this
class.
"""

from deckr.core.exceptions import FailedRestrictionException, TooManyPlayers
from deckr.core.game_object import GameObject
from deckr.core.player import Player
from deckr.core.zone import HasZones


def action(params=None, restrictions=None):
    """
    A simple decorator to define an action. This takes in an optional list
    of restrictions. These will be run before the function. If these fail
    they should raise an appropriate FailedRestrictionException.
    """

    if restrictions is None:
        restrictions = []
    if params is None:
        params = {}
    # pylint: disable=missing-docstring

    def wrapper(func):
        def inner(*args, **kwargs):
            for res in restrictions:
                res(*args, **kwargs)
            return func(*args, **kwargs)
        inner.action = True
        # py3k (using annotaions)
        # inner.__annotations__ = func.__annotations__
        # python 2.7 (faking annotations)
        inner.__annotations__ = params
        return inner
    return wrapper


def restriction(desciption):
    """
    A simple decorator that can be applied to restrictions. Restrictions
    must return a Boolean. If this is false, the decorator will raise an
    exception describing what went wrong.
    """

    # pylint: disable=missing-docstring
    def wrapper(func):
        def inner(*args, **kwargs):
            if not func(*args, **kwargs):
                raise FailedRestrictionException(desciption)
        return inner
    return wrapper


def operate_on_list_or_single(singleton_function, obj, **kwargs):
    """
    This will allow functions to operate on either lists or singletons. It
    will simply do an isinstance check and then delegate properly to the
    singleton_function. Output is returned in either a list or singelton.
    """

    if isinstance(obj, list):
        return [singleton_function(x, **kwargs) for x in obj]
    else:
        return singleton_function(obj, **kwargs)


class Game(GameObject, HasZones):  # pylint: disable=abstract-class-not-used

    """
    The Game class provides the core logic behind any game: making actions
    and processing updates.
    """

    game_object_type = 'Game'
    max_players = None
    game_zones = []
    player_zones = []

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)

        self.game_objects = {}
        self.transitions = {}
        self.players = []
        self.next_game_id = 0

        self.register(self)
        self.load_zones(self.game_zones)
        for zone in self.zones.values():
            zone.set_game_attribute('owner', self.game)

    ######################
    # External Functions #
    ######################

    def set_up(self):
        """
        Overriden by subclasses.
        """

        raise NotImplementedError

    def get_all_transitions(self):
        """
        Get all the current transitions.
        """

        return [(player, self.get_transitions(player))
                for player in self.players]

    def flush_all_transitions(self):
        """
        Flush all transitions.
        """

        self.transitions = {}

    def get_transitions(self, player):
        """
        Get the transitions for a given player.
        """

        return self.transitions.get(player, [])

    def add_transition(self, transition, player=None):
        """
        Add a transition to this game.
        """

        if player is not None:
            self.transitions.setdefault(player, []).append(transition)
        else:
            for player in self.players:
                self.add_transition(transition, player)

    def get_state(self, player=None):
        """
        Gets the current state of the game for a specific player. If player is
        None will only return information that is public knowledge.
        """

        return [value.serialize(player)
                for value in self.game_objects.values()]

    def add_player(self):
        """
        Adds a new player if possible. Raises TooManyPlayers if there are
        already too many players. Returns the newly created player.
        """

        if (self.max_players is not None and
                len(self.players) >= self.max_players):
            raise TooManyPlayers
        player = Player()
        player.load_zones(self.player_zones)
        self.register(player)
        self.register(player.zones.values())
        for zone in player.zones.values():
            zone.set_game_attribute('owner', player)
        self.players.append(player)
        return player

    ######################
    # Internal Functions #
    ######################

    def register_single(self, obj):
        """
        Registers a single object.
        """

        if obj.game_id is None:
            game_id = self.next_game_id
            self.game_objects[game_id] = obj
            obj.game_id = game_id
            obj.game = self
            self.next_game_id += 1
            return game_id
        else:
            return obj.game_id

    def deregister_single(self, obj):
        """
        Deregister a single object.
        """

        if obj.game_id is not None:
            del self.game_objects[obj.game_id]
            obj.game_id = None

    def get_object_single(self, obj_id, klass):
        """
        Gets a single object.
        """

        result = self.game_objects.get(obj_id, None)
        if klass is not None and not isinstance(result, klass):
            raise ValueError(
                "Expected a {0} but got {1}".format(
                    klass,
                    result))
        return result

    def register(self, obj):
        """
        Registers a game object. This will assign it a game id and make it
        possible for the game to lookup this object. Can take in either a list
        or a singleton. Will return the game_ids generated.
        """

        return operate_on_list_or_single(self.register_single, obj)

    def deregister(self, obj):
        """
        Dergisters a game object. Removes the object from internal storage, and
        sets the id to None. Will skip over objects that are not registered.
        Can take in either a list or a singleton.
        """

        return operate_on_list_or_single(self.deregister_single, obj)

    def get_object(self, obj_id, klass=None):
        """
        Looks up and object by its id. Returns the object if present, or None
        otherwise. Can operate on either a list or a singleton.
        """

        return operate_on_list_or_single(self.get_object_single, obj_id,
                                         klass=klass)

    #############
    # Callbacks #
    #############

    def post_add_zone_callback(self, zone):
        """
        After we get a zone we want to register it.
        """

        self.register(zone)
