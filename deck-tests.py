import unittest

import deck
from deck import Deck, Card, Hand


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
        assert c1.value == deck.Value.Joker

    def test_format(self):
        c1 = Card("♥", 9)
        c2 = Card("Diamonds", "King")
        c3 = Card(joker=True)
        assert format(c1) == "9♥"
        assert format(c2) == "K♦"
        assert format(c3) == "Jok"

        assert format(c1, "<4") == "9♥  "
        assert format(c2, "<4") == "King♦"
        assert format(c3, "<4") == "Joker"
        assert format(c1, ">7") == "     9♥"
        assert format(c2, ">7") == "  King♦"
        assert format(c3, ">7") == "  Joker"
        assert format(c1, "<5.5") == "9♥   "
        assert format(c2, "<5.5") == "King♦"
        assert format(c3, "<5.5") == "Joker"


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
        h1 = deck.get_poker_hand(
            cards + [Card("Diamonds", 7), Card("Diamonds", "Queen")]
        )
        h2 = deck.get_poker_hand(cards + [Card("Hearts", 2), Card("Diamonds", "Jack")])
        assert h1 > h2


class HandTests(unittest.TestCase):
    HAND1 = Hand(
        Card("♥", 2), Card("♦", 11), Card("♥", 3), Card(joker=True), Card("♠", 11)
    )
    HAND2 = Hand(
        Card("♦", 2), Card("♥", 11), Card("♠", 3), Card(joker=True), Card("♠", 11)
    )

    def test_type_checks(self):
        with Hand.runtime_type_checks():
            try:
                Hand(["!not a card!"])
            except ValueError as ex:
                assert "!not a card!" in str(ex)
            else:
                assert False, "expected runtime error"

        with Hand.runtime_type_checks(False):
            try:
                Hand("!not a card!")
            except ValueError as ex:
                assert False, "expected no error"

    def test_deal(self):
        deck = Deck()
        hands = deck.deal_hands()
        assert len(hands) == 2
        assert len(hands[0]) == 5
        assert len(hands[1]) == 5

    def test_default_sort(self):
        hand = Hand(self.HAND1)
        hand.sort(deck.HandSort.Default)
        assert [c.value.value for c in hand] == [2, 3, 11, 11, 15]
        hand.sort(deck.HandSort.Default, reverse=True)
        assert [c.value.value for c in hand] == [15, 11, 11, 3, 2]

    def test_sort_suit(self):
        hand = Hand(Card("♦", 2), Card("♠", 2), Card("♣", 2), Card("♥", 2))
        hand.sort(deck.HandSort.Default)
        assert "".join(c.suit.value for c in hand) == "♣♦♥♠"
        hand.sort(deck.HandSort.Default, reverse=True)
        assert "".join(c.suit.value for c in hand) == "♠♥♦♣"

    def test_poker_sort(self):
        hand = Hand(self.HAND1)
        hand.sort(deck.HandSort.Poker)
        assert [c.value.value for c in hand] == [2, 3, 15, 11, 11]
        hand.sort(deck.HandSort.Poker, reverse=True)
        assert [c.value.value for c in hand] == [11, 11, 15, 3, 2]

    def test_intersect_exact(self):
        hand1, hand2 = self.HAND1, self.HAND2
        # Self-intersect should be the complete set
        assert set(hand1.intersect(hand1, deck.HandComparison.Exact)) == set(hand1)
        assert set(hand2.intersect(hand2, deck.HandComparison.Exact)) == set(hand2)
        # Only exact matches should remain after an intersect
        assert set(hand1.intersect(hand2, deck.HandComparison.Exact)) == {
            Card(joker=True),
            Card("♠", 11),
        }

    def test_intersect_value(self):
        hand1, hand2 = self.HAND1, self.HAND2
        hand3 = Hand(Card("♥", 11))
        expect_hand3 = {Card("♦", 11), Card("♠", 11)}
        hand4 = Hand(Card(joker=True))
        with Hand.default_comparison(deck.HandComparison.Values):
            # Self-intersect should be the complete set
            assert set(hand1.intersect(hand1)) == set(hand1)
            assert set(hand2.intersect(hand2)) == set(hand2)
            # All values exist between hand1 and hand2 and so we get all of them
            assert set(hand1.intersect(hand2)) == set(hand1)
            # Only Jacks are retained
            assert set(hand1.intersect(hand3)) == expect_hand3
            # Only Jokers are retained
            assert set(hand1.intersect(hand4)) == set(hand4)
            # Check bitwise operator
            assert set(hand1 & hand3) == expect_hand3
            # Check in-place operator
            h1 = Hand(hand1)
            h1 &= hand3
            assert set(h1) == expect_hand3
            assert len(hand1) != len(h1)

    def test_intersect_suit(self):
        hand1, hand2 = self.HAND1, self.HAND2
        hand3 = Hand(Card("♥", 11))
        expect_hand3 = {Card("♥", 2), Card("♥", 3)}
        hand4 = Hand(Card(joker=True))
        with Hand.default_comparison(deck.HandComparison.Suits):
            # Self-intersect should be the complete set
            assert set(hand1.intersect(hand1)) == set(hand1)
            assert set(hand2.intersect(hand2)) == set(hand2)
            # All suits exist between hand1 and hand2 and so we get all of them
            assert set(hand1.intersect(hand2)) == set(hand1)
            # Only Hearts are retained
            assert set(hand1.intersect(hand3)) == expect_hand3
            # Only Jokers are retained
            assert set(hand1.intersect(hand4)) == set(hand4)
            # Check bitwise operator
            assert set(hand1 & hand3) == expect_hand3
            # Check in-place operator
            h1 = Hand(hand1)
            h1 &= hand3
            assert set(h1) == expect_hand3
            assert len(hand1) != len(h1)

    def test_union_exact(self):
        hand1, hand2 = self.HAND1, self.HAND2
        # Self-union should be the original hand
        assert list(hand1.union(hand1, deck.HandComparison.Exact)) == list(hand1)
        assert list(hand2.union(hand2, deck.HandComparison.Exact)) == list(hand2)
        # Exact matches should not duplicate after a union
        assert list(hand1.union(hand2, deck.HandComparison.Exact)) == [
            *hand1,
            *hand2[:3],
        ]

    def test_union_value(self):
        hand1, hand2 = self.HAND1, self.HAND2
        hand3 = Hand(Card("♥", 10), Card("♥", 11))
        expect_hand3 = [*hand1, hand3[0]]
        hand4 = Hand(Card(joker=True))
        with Hand.default_comparison(deck.HandComparison.Values):
            # Self-union should be the complete list
            assert list(hand1.union(hand1)) == list(hand1)
            assert list(hand2.union(hand2)) == list(hand2)
            # All values exist between hand1 and hand2 and so we get all of them
            assert list(hand1.union(hand2)) == list(hand1)
            # Only Tens are added
            assert list(hand1.union(hand3)) == expect_hand3
            # Nothing is added
            assert list(hand1.union(hand4)) == list(hand1)
            # Check bitwise operator
            assert list(hand1 | hand3) == expect_hand3
            # Check in-place operator
            h1 = Hand(c for c in hand1 if c.value == 3)
            h1 |= hand1
            assert set(h1) == set(hand1)

    def test_union_suit(self):
        hand1, hand2 = self.HAND1, self.HAND2
        hand3 = Hand(Card("♥", 10), Card("♥", 11))
        expect_hand3 = [*hand1, *hand3]
        hand4 = Hand(Card(joker=True))
        with Hand.default_comparison(deck.HandComparison.Suits):
            # Self-union should be the complete hand
            assert list(hand1.union(hand1)) == list(hand1)
            assert list(hand2.union(hand2)) == list(hand2)
            # All suits exist between hand1 and hand2 and so we get all of them
            assert list(hand1.union(hand2)) == list(hand1)
            # Nothing is added
            assert list(hand1.union(hand3)) == list(hand1)
            # Nothing is added
            assert list(hand1.union(hand4)) == list(hand1)
            # Check bitwise operator
            assert list(hand1 | hand3) == list(hand1)
            # Check in-place operator
            h1 = Hand(c for c in hand1 if c.suit != deck.Suit.Hearts)
            h1 |= hand1
            assert set(h1) == set(hand1)


if __name__ == "__main__":
    unittest.main()
