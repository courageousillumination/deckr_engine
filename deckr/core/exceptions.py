"""
This module provides all the exceptions used by the core deckr engine.
"""


class FailedRestrictionException(Exception):

    """
    This exception should be raised whenever a restriction test is failed.
    """

    pass


class TooManyPlayers(Exception):

    """
    Raised when someone tries to join a game that already has the maximum
    number of players.
    """

    pass
