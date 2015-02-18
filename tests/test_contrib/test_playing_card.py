"""
Test the functionality related to playing cards.
"""

from unittest import TestCase

from deckr.contrib.playing_card import create_deck, PlayingCard, SUITS


class UtilityTestCase(TestCase):

    """
    This will tests all of the utility functions related to playing cards.
    """

    def test_create_deck(self):
        """
        Make sure that we can properly create a deck of cards.
        """

        deck = create_deck()
        self.assertEqual(len(deck), 52)
        for i in range(1, 14):
            for suit in SUITS:
                self.assertIn(PlayingCard(i, suit), deck)


class PlayingCardTestCase(TestCase):

    """
    Test the basic functionality of a playing card.
    """

    def test_equality(self):
        """
        Test that we can check for card equality.
        """

        self.assertEqual(PlayingCard(1, 'hearts'), PlayingCard(1, 'hearts'))
        self.assertNotEqual(PlayingCard(1, 'hearts'), PlayingCard(1, 'clubs'))
        self.assertNotEqual(PlayingCard(1, 'hearts'), PlayingCard(2, 'hearts'))
