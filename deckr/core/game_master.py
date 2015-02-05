class GameMaster(object):

    def __init__(self):
        self.game_types = {}
        self.games = {}
        self.game_type_id = 0
        self.game_id = 0

    def register(self, game_path):
        self.game_types[self.game_type_id] = game_path
        self.game_type_id += 1
        return self.game_type_id - 1

    def create(self, game_type_id):
        game_definition = self.game_types[game_type_id]
        self.games[self.game_id] = None
        self.game_id += 1
        return self.game_id - 1

    def list_game_types(self):
        return self.game_types.items()
