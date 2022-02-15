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


class PokerHandTests(unittest.TestCase):
    def test_high_card(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 5),
            Card("Diamonds", 7),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.HighCard, 9, 7, 5, 4, 2)

    def test_high_card_ace(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 5),
            Card("Diamonds", 7),
            Card("Spades", "Ace"),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.HighCard, 14, 7, 5, 4, 2)

    def test_pair(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 5),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.Pair, 9, 5)

    def test_two_pair(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 5),
            Card("Hearts", 5),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.TwoPair, 9, 5)

    def test_triples(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 9),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.ThreeOfAKind, 9, 4)

    def test_straight(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 3),
            Card("Hearts", 4),
            Card("Diamonds", 5),
            Card("Spades", 6),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.Straight, 6)

    def test_flush(self):
        cards = [
            Card("Clubs", 2),
            Card("Clubs", 4),
            Card("Clubs", 5),
            Card("Clubs", 7),
            Card("Clubs", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.Flush, 9)

    def test_full_house(self):
        cards = [
            Card("Spades", 4),
            Card("Clubs", 4),
            Card("Hearts", 9),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.FullHouse, 9)

    def test_fours(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 9),
            Card("Hearts", 9),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.FourOfAKind, 9)

    def test_straight_flush(self):
        cards = [
            Card("Clubs", 5),
            Card("Clubs", 6),
            Card("Clubs", 7),
            Card("Clubs", 8),
            Card("Clubs", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.StraightFlush, 9)

    def test_compare_1(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 5),
            Card("Diamonds", 7),
        ]
        h1 = deck.get_poker_hand(cards + [Card("Spades", "Ace")])
        h2 = deck.get_poker_hand(cards + [Card("Spades", "King")])
        assert h1 > h2

    def test_compare_2(self):
        cards = [
            Card("Spades", 6),
            Card("Hearts", 2),
            Card("Clubs", "King"),
        ]
        h1 = deck.get_poker_hand(cards + [Card("Diamonds", 8), Card("Diamonds", "Ace")])
        h2 = deck.get_poker_hand(cards + [Card("Spades", 9), Card("Diamonds", 5)])
        assert h1 > h2

    def test_compare_3(self):
        cards = [
            Card("Diamonds", 6),
            Card("Spades", 9),
            Card("Clubs", "King"),
        ]
        h1 = deck.get_poker_hand(cards + [Card("Diamonds", 7), Card("Diamonds", "Queen")])
        h2 = deck.get_poker_hand(cards + [Card("Hearts", 2), Card("Diamonds", "Jack")])
        assert h1 > h2

if __name__ == "__main__":
    unittest.main()
