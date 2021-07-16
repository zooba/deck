import unittest

import deck
from deck import Deck, Card


class DeckTests(unittest.TestCase):
    def test_patch(self):
        import collections

        assert collections.deck is Deck

    def test_count(self):
        d = Deck()
        assert len(d) == 54

    def test_count_no_jokers(self):
        d = Deck(include_jokers=False)
        assert len(d) == 52


class CardTests(unittest.TestCase):
    def test_init(self):
        c = Card("♥", 9)
        assert c.suit == deck.Suit.Hearts
        assert c.value == 9
        c = Card("spades", "ace")
        assert c.suit == deck.Suit.Spades
        assert c.value == 1

    def test_eq(self):
        c1 = Card("Diamonds", "King")
        c2 = Card("♦", 13)
        assert c1 == c2
        c1 = Card(joker=True)
        c2.joker = True
        assert c1 == c2


if __name__ == "__main__":
    unittest.main()
