"""Implementation of the deck collection type."""

__version__ = "3.0.0"

import collections
import enum
import itertools
import random


class Suit(enum.Enum):
    Hearts = "♥"
    Spades = "♠"
    Clubs = "♣"
    Diamonds = "♦"


class Value(enum.IntEnum):
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13


class PokerHand(enum.IntEnum):
    HighCard = 1
    Pair = 2
    TwoPair = 3
    ThreeOfAKind = 4
    Straight = 5
    Flush = 6
    FullHouse = 7
    FourOfAKind = 8
    StraightFlush = 9
    FiveOfAKind = 10


def _from_enum(enm, v):
    try:
        return enm(v)
    except ValueError:
        pass
    try:
        return getattr(enm, v)
    except AttributeError:
        try:
            return getattr(enm, str(v).capitalize())
        except AttributeError:
            pass
    return enm(v)


class Card:
    def __init__(self, suit=None, value=None, joker=False):
        self.joker = joker
        if self.joker:
            self.suit, self.value = None, None
        else:
            if value is None:
                suit, value = suit
            self.suit = _from_enum(Suit, suit)
            self.value = _from_enum(Value, value)

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        if self.joker and other.joker:
            return True
        return other.suit == self.suit and other.value == self.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1337 if self.joker else hash((self.suit, self.value))

    def __repr__(self):
        return (
            "Card(joker=True)" if self.joker else f"Card({self.suit!r}, {self.value!r})"
        )

    def __str__(self):
        return "Joker" if self.joker else f"{self.value.value}{self.suit.value}"


class Deck(collections.deque):
    def __init__(self, include_jokers=True):
        super().__init__(
            map(
                Card,
                itertools.product(
                    Suit.__members__.values(), Value.__members__.values()
                ),
            )
        )
        if include_jokers:
            self.append(Card(joker=True))
            self.append(Card(joker=True))

    def shuffle(self, rng=random):
        rng.shuffle(self)

    deal = collections.deque.pop

    deal_from_bottom = collections.deque.popleft


def aces_high(card):
    """A sort key function to sort aces high."""
    if isinstance(card, Value):
        if card == Value.Ace:
            return 14
        return card.value

    if card.joker:
        raise ValueError("Wildcards are not supported")
    if card.value == Value.Ace:
        return 14
    return card.value.value


def get_poker_hand(cards):
    """Given a sequence of cards, returns the best possible poker hand.

    The return value is a tuple of a member of `PokerHand` and `Value`,
    where the value is the highest card. These tuples may be compared
    against each other to determine the best among a set of hands.
    The best hand sorts last (is greater than other hands).
    """
    cards = sorted(cards, key=aces_high, reverse=True)

    if len(cards) > 5:
        return max(map(get_poker_hand, itertools.combinations(cards, 5)))

    cvalues = collections.Counter(c.value for c in cards)
    suits = set(c.suit for c in cards)
    of_a_kind_card, of_a_kind = cvalues.most_common(1)[0]
    if len(cvalues) >= 2:
        second_pair_card, second_pair = cvalues.most_common(2)[-1]
    else:
        second_pair_card, second_pair = None, 0
    high_card = cards[0].value
    values = [c.value.value for c in cards]
    is_straight = len(cards) == 5 and all(
        i[0].value == i[1] for i in zip(cards, range(cards[0].value, -5, -1))
    )

    if len(suits) == 1 and is_straight:
        return PokerHand.StraightFlush, aces_high(high_card)
    if of_a_kind == 4:
        return PokerHand.FourOfAKind, aces_high(of_a_kind_card)
    if of_a_kind == 3 and second_pair == 2:
        return PokerHand.FullHouse, aces_high(of_a_kind_card)
    if len(suits) == 1 and len(cards) == 5:
        return PokerHand.Flush, aces_high(high_card)
    if is_straight:
        return PokerHand.Straight, aces_high(high_card)
    if of_a_kind == 3:
        return (PokerHand.ThreeOfAKind, aces_high(of_a_kind_card)) + (
            (aces_high(second_pair_card),) if second_pair_card else ()
        )
    if of_a_kind == 2 and second_pair == 2:
        return (PokerHand.TwoPair,) + tuple(
            map(
                aces_high,
                sorted(
                    filter(None, (of_a_kind_card, second_pair_card)),
                    reverse=True,
                    key=aces_high,
                ),
            )
        )
    if of_a_kind == 2:
        return (PokerHand.Pair, aces_high(of_a_kind_card)) + (
            (aces_high(second_pair_card),) if second_pair_card else ()
        )

    return (PokerHand.HighCard,) + tuple(
        sorted((aces_high(c) for c in cvalues), reverse=True)
    )


collections.deck = Deck
