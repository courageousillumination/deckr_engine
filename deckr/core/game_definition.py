"""
This file provides the GameDefinition class.
"""

import os
import sys

import yaml


class GameDefinition(object):

    """
    A game definition includes all the core information for a game.
    """

    def __init__(self):
        self.config = None
        self.klass = None
        self.name = None

    def load(self, path):
        """
        Load a game definition from a specified path.
        """

        config_file = open(os.path.join(path, 'config.yml'))
        self.config = yaml.load(config_file)

        if 'game_file' not in self.config or 'game_class' not in self.config:
            raise ValueError(
                "Configuration file is missing required attributes.")

        # Add the super directory to the system path
        sys.path.append(path)
        # Explicitly import our game as the game object
        game_module = __import__(self.config['game_file'])
        # Clean up the system path that we don't care about any more.
        sys.path.remove(path)

        # Load the class
        self.klass = getattr(game_module, self.config['game_class'])

        # Load other useful attributes
        self.name = self.config.get('name', 'Unnamed Game')

    def create_instance(self):
        """
        Create a game using this game definition.
        """

        return self.klass()
