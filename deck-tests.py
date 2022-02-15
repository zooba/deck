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
        assert hand == (deck.PokerHand.HighCard, deck.Value.Nine)

    def test_high_card_ace(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 5),
            Card("Diamonds", 7),
            Card("Spades", "Ace"),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.HighCard, deck.Value.Ace)

    def test_pair(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 5),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.Pair, deck.Value.Nine, deck.Value.Five)

    def test_two_pair(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 5),
            Card("Hearts", 5),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.TwoPair, deck.Value.Nine, deck.Value.Five)

    def test_triples(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 4),
            Card("Hearts", 9),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.ThreeOfAKind, deck.Value.Nine, deck.Value.Four)

    def test_straight(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 3),
            Card("Hearts", 4),
            Card("Diamonds", 5),
            Card("Spades", 6),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.Straight, deck.Value.Six)

    def test_flush(self):
        cards = [
            Card("Clubs", 2),
            Card("Clubs", 4),
            Card("Clubs", 5),
            Card("Clubs", 7),
            Card("Clubs", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.Flush, deck.Value.Nine)

    def test_full_house(self):
        cards = [
            Card("Spades", 4),
            Card("Clubs", 4),
            Card("Hearts", 9),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.FullHouse, deck.Value.Nine)

    def test_fours(self):
        cards = [
            Card("Spades", 2),
            Card("Clubs", 9),
            Card("Hearts", 9),
            Card("Diamonds", 9),
            Card("Spades", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.FourOfAKind, deck.Value.Nine)

    def test_straight_flush(self):
        cards = [
            Card("Clubs", 5),
            Card("Clubs", 6),
            Card("Clubs", 7),
            Card("Clubs", 8),
            Card("Clubs", 9),
        ]
        hand = deck.get_poker_hand(cards)
        assert hand == (deck.PokerHand.StraightFlush, deck.Value.Nine)


if __name__ == "__main__":
    unittest.main()
