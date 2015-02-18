"""
A simple class + utility functions for playing cards.
"""

from deckr.contrib.card import Card

SUITS = ['clubs', 'spades', 'hearts', 'diamonds']


def create_deck():
    """
    Creates a deck of playing cards. Does not include jokers.
    """

    return [PlayingCard(num, suit) for num in range(1, 14) for suit in SUITS]


class PlayingCard(Card):

    """
    Represents a playing card with a suit and a number.
    """

    def __init__(self, number, suit):
        super(PlayingCard, self).__init__()
        self.number = number
        self.suit = suit

        # Calculate the card ID
        if self.number == 1:
            card_id = SUITS.index(suit) + 1
        else:
            card_id = (14 - number) * 4 + SUITS.index(suit) + 1
        self.set_game_attribute('card_id', card_id)
        self.set_game_attribute('number', number)
        self.set_game_attribute('suit', suit)

    def __eq__(self, other):
        return self.number == other.number and self.suit == other.suit
