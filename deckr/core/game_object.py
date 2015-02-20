"""
This files provides the GameObject class.
"""


def clean_game_objects(obj):
    """
    Clean up game objects for serialization.
    """

    if isinstance(obj, list):
        return [clean_game_objects(x) for x in obj]
    elif isinstance(obj, dict):
        return {clean_game_objects(key): clean_game_objects(value) for
                key, value in obj.items()}
    elif isinstance(obj, GameObject):
        return obj.game_id
    return obj


class GameObject(object):

    """
    A game object can represent an arbitrary object in the game (a card,
    a board tile, etc).
    """

    game_object_type = 'GameObject'

    def __init__(self, *args, **kwargs):
        super(GameObject, self).__init__(*args, **kwargs)
        # Specifies the id of this object
        self.game_id = None
        self.game = None
        self.game_attributes = {}
        self.player_overrides = {}

    def serialize(self, player=None):
        """
        This function will convert this object to a dictionary that can be
        transmitted over some kind of network (i.e. all internal references
        have been removed).
        """

        result = {key: self.get_game_attribute(key, player) for
                  key in self.game_attributes}
        result['game_id'] = self.game_id
        result['type'] = self.game_object_type
        return clean_game_objects(result)

    def set_game_attribute(self, name, value, player=None):
        """
        Sets a specific game attribute. These will be tracked and sent out in
        updates/the game state.
        """

        if player is not None:
            self.player_overrides.setdefault(player, {})[name] = value
        else:
            self.game_attributes[name] = value

        # Register the change with my game.
        if self.game is not None:
            self.game.add_transition({"update_type": "set", "game_object": self,
                                      "field": name, "value": value}, player)

    def get_game_attribute(self, name, player=None):
        """
        Gets a specific game attribute. Throws an AttributeError if the
        attribute doesn't exist.
        """

        if player is not None:
            try:
                return self.player_overrides[player][name]
            except KeyError:
                pass
        try:
            return self.game_attributes[name]
        except KeyError:
            error = 'Could not find game attribute {0}'.format(name)
            raise AttributeError(error)
