from deckr.core.game import action, Game
from deckr.core.game_object import GameObject


class SimpleGame(Game):

    def __init__(self):
        super(SimpleGame, self).__init__()
        self.ran_test_action = False
        self.game_object = None
        self.test_parameter = None

    def set_up(self):
        self.game_object = GameObject()
        self.register(self.game_object)

    @action()
    def test_action(self, player):
        self.ran_test_action = True

    @action()
    def test_update_action(self, player):
        self.game_object.set_game_attribute('foo', 'bar')

    @action(params={'game_object': GameObject})
    def test_parameter_action(self, player, game_object):
        self.test_parameter = game_object
