"""
A simple class + utility functions for playing cards.
"""

from deckr.contrib.card import Card

SUITS = ['clubs', 'diamonds', 'hearts', 'spades']


def create_deck():
    """
    Creates a deck of playing cards. Does not include jokers.
    """

    return [PlayingCard(num, suit) for num in range(13) for suit in SUITS]


class PlayingCard(Card):

    """
    Represents a playing card with a suit and a number.
    """

    def __init__(self, number, suit):
        super(PlayingCard, self).__init__()
        self.number = number
        self.suit = suit

        # Calculate the card ID
        self.set_game_attribute('card_id', number + SUITS.index(suit) * 13 + 1)

    def __eq__(self, other):
        return self.number == other.number and self.suit == other.suit
