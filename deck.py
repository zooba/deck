"""Implementation of the deck collection type."""

__version__ = "3.1.0b1"

import collections
import contextvars
import enum
import itertools
import random
import sys

__all__ = [
    "Card",
    "Deck",
    "get_poker_hand",
    "Hand",
    "HandComparison",
    "HandSort",
    "PokerHand",
    "Suit",
    "Value",
]

_SUIT_SORT_ORDER = {
    # Handle suit-less comparisons gracefully (as highest)
    "": 10,
    None: 10,
    # Suits in bridge ordering
    "♠": 3,
    "♥": 2,
    "♦": 1,
    "♣": 0,
}


class Suit(enum.Enum):
    Hearts = "♥"
    Spades = "♠"
    Clubs = "♣"
    Diamonds = "♦"

    def __lt__(self, other):
        x1 = _SUIT_SORT_ORDER[self.value]
        try:
            x2 = _SUIT_SORT_ORDER[other.value]
        except LookupError:
            x2 = _SUIT_SORT_ORDER[_from_enum(Suit, other).value]
        return x1 < x2

    def __gt__(self, other):
        x1 = _SUIT_SORT_ORDER[self.value]
        try:
            x2 = _SUIT_SORT_ORDER[other.value]
        except LookupError:
            x2 = _SUIT_SORT_ORDER[_from_enum(Suit, other).value]
        return x1 > x2

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return self == other or self > other


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
    Joker = 15


# A mapping from enum values to "nice" names. Only names longer than one
# character are included, with suitable abbreviations. Users of this map
# should select the first name from the list of suitable length. Missing
# values should use str(int(v)) of the value.
_VALUE_STR_MAP = {
    Value.Ace: ["Ace", "A"],
    Value.King: ["King", "Kng", "K"],
    Value.Queen: ["Queen", "Que", "Q"],
    Value.Jack: ["Jack", "Jck", "J"],
    Value.Ten: ["10", "X"],
    Value.Joker: ["Joker", "Jok", "🤡"],
}


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
    if isinstance(v, str):
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
    """Represents a single playing card in the Deck.

    The 'suit' and 'value' may be provided as enum members or strings
    (with case-insensitive names of the enum members). Values may
    additionally be provided as integers.

    >>> c = Card(Suit.Diamonds, Value.Nine)
    >>> c = Card('diamonds', 'nine')
    >>> c = Card('♦', 9)

    Specifying 'joker' as True will create a joker card, ignoring the
    other arguments. Jokers do not have a suit, and coloured/black and
    white cannot be distinguished.

    >>> c = Card(joker=True)

    While not enforced, a Card is assumed to be an immutable constant,
    and instances may be reused even when representing "physically"
    distinct cards. Do not modify Card instances directly.
    """

    def __init__(self, suit=None, value=None, joker=False):
        if joker:
            self.suit, self.value, self.joker = None, Value.Joker, True
        else:
            if value is None:
                suit, value = suit
            self.suit = _from_enum(Suit, suit)
            self.value = _from_enum(Value, value)
            self.joker = self.value == Value.Joker

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
        return format(self, ".")

    def __format__(self, spec):
        justify, _, width = (spec or ".3").partition(".")
        width = int(width or 0)
        if self.joker:
            for s in _VALUE_STR_MAP[Value.Joker]:
                if not width or len(s) <= width:
                    break
        else:
            # We include the suit character after the value
            for s in _VALUE_STR_MAP.get(self.value) or [str(int(self.value))]:
                if not width or len(s) < width:
                    break
            s = f"{s}{self.suit.value}"
        return format(s, justify)


class Deck(collections.deque):
    """Represents a deck of cards."""

    def __init__(self, include_jokers=True, *, decks=1):
        if decks < 0:
            raise ValueError("'decks' cannot be negative")
        super().__init__()
        if decks:
            cards = [
                Card(i)
                for i in itertools.product(
                    Suit.__members__.values(),
                    (v for v in Value.__members__.values() if v != Value.Joker),
                )
            ]
            if include_jokers:
                cards.extend([Card(joker=True)] * 2)
            for _ in range(decks):
                self.extend(cards)

    def shuffle(self, random=random):
        random.shuffle(self)

    deal = collections.deque.pop

    deal_from_bottom = collections.deque.popleft

    def deal_hands(self, hands=2, cards=5):
        if hands * cards > len(self):
            raise ValueError(
                "not enough cards to deal {} hands of {}".format(hands, cards)
            )
        hand = [Hand() for _ in range(hands)]
        for _ in range(cards):
            for h in hand:
                h.append(self.deal())
        return hand


def aces_high(card):
    """A sort key function to sort aces high.

    This is not used with the Hand class, but is a low-level helper for
    when dealing with builtin collections of Card or Value values.

    h = sorted(list_of_cards, key=aces_high)"""
    if isinstance(card, Value):
        if card == Value.Ace:
            return 14
        return card.value

    if card.joker:
        return 15
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
    cards_low_ace = sorted(cards, key=lambda card: card.value, reverse=True)

    # Any jokers will have sorted to the front
    if cards and cards[0].joker:
        raise ValueError("Cannot calculate poker hand including jokers")

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
    is_ace_low_straight = len(cards) == 5 and all(
        i[0].value == i[1]
        for i in zip(cards_low_ace, range(cards_low_ace[0].value, -5, -1))
    )

    if len(suits) == 1 and is_straight:
        return PokerHand.StraightFlush, aces_high(high_card)
    if len(suits) == 1 and is_ace_low_straight:
        return PokerHand.StraightFlush, cards_low_ace[0].value
    if of_a_kind == 4:
        return PokerHand.FourOfAKind, aces_high(of_a_kind_card)
    if of_a_kind == 3 and second_pair == 2:
        return PokerHand.FullHouse, aces_high(of_a_kind_card)
    if len(suits) == 1 and len(cards) == 5:
        return PokerHand.Flush, aces_high(high_card)
    if is_straight:
        return PokerHand.Straight, aces_high(high_card)
    if is_ace_low_straight:
        return PokerHand.Straight, cards_low_ace[0].value
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


class HandSort(enum.Enum):
    Default = "default"
    Poker = "poker"
    AcesHigh = "aces_high"
    Unsorted = "unsorted"


class HandComparison(enum.Enum):
    Exact = "exact"
    Values = "values"
    Suits = "suits"


_HAND_ORDER = contextvars.ContextVar("Hand.default_sort")
_HAND_ORDER.set(HandSort.Default)

_HAND_CMP = contextvars.ContextVar("Hand.default_comparison")
_HAND_CMP.set(HandComparison.Exact)


class Hand(list):
    """Represents a hand of cards.

    Used for conveniently comparing and displaying hands.

    Hands support format() spec '<justification>.<width><order>',
    where justification is an optional '<', '>' or '^' prefix followed
    by the number of columns, and width is the maximum number of
    characters to use when representing each card. The optional 'order'
    specifier is either 'asc' or 'desc', to sort cards for display.
    """

    def check_contents(self):
        invalid = [c for c in self if not isinstance(c, Card)]
        if invalid:
            raise ValueError(
                "invalid objects in hand: {}".format(
                    ", ".join(repr(c) for c in invalid)
                )
            )

    def index(self, card_suit_or_value, start=0, stop=sys.maxsize):
        """Locate the first matching card, suit or value."""
        # Being passed a whole card is our fast path
        if isinstance(card_suit_or_value, Card):
            cmp = _HAND_CMP.get()
            if cmp == HandComparison.Exact:
                return super().index(card_suit_or_value, start, stop)
            elif cmp == HandComparison.Values:
                card_suit_or_value = card_suit_or_value.value
            elif cmp == HandComparison.Suits:
                card_suit_or_value = card_suit_or_value.suit
            else:
                raise ValueError("unable to compare with {}".format(cmp))

        # Convert int or str to enum types transparently
        if isinstance(card_suit_or_value, int):
            try:
                card_suit_or_value = _from_enum(Value, card_suit_or_value)
            except ValueError:
                pass
        elif isinstance(card_suit_or_value, str):
            try:
                card_suit_or_value = _from_enum(Suit, card_suit_or_value)
            except ValueError:
                try:
                    card_suit_or_value = _from_enum(Value, card_suit_or_value)
                except ValueError:
                    pass

        # If we now have a searchable type, search for it
        if isinstance(card_suit_or_value, Value):
            for i, c in enumerate(self):
                if start <= i < stop and c.value == card_suit_or_value:
                    return i
        elif isinstance(card_suit_or_value, Suit):
            for i, c in enumerate(self):
                if start <= i < stop and c.suit == card_suit_or_value:
                    return i
        raise ValueError(f"{card_suit_or_value!r} is not in hand")

    def count(self, card_suit_or_value):
        """Count the number of matching cards, suits or values."""
        # Being passed a whole card is our fast path
        if isinstance(card_suit_or_value, Card):
            cmp = _HAND_CMP.get()
            if cmp == HandComparison.Exact:
                return super().count(card_suit_or_value)
            elif cmp == HandComparison.Values:
                card_suit_or_value = card_suit_or_value.value
            elif cmp == HandComparison.Suits:
                card_suit_or_value = card_suit_or_value.suit
            else:
                raise ValueError("unable to compare with {}".format(cmp))

        # Convert int or str to enum types transparently
        if isinstance(card_suit_or_value, int):
            try:
                card_suit_or_value = _from_enum(Value, card_suit_or_value)
            except ValueError:
                pass
        elif isinstance(card_suit_or_value, str):
            try:
                card_suit_or_value = _from_enum(Suit, card_suit_or_value)
            except ValueError:
                try:
                    card_suit_or_value = _from_enum(Value, card_suit_or_value)
                except ValueError:
                    pass

        # If we now have a searchable type, search for it
        if isinstance(card_suit_or_value, Value):
            return sum(c.value == card_suit_or_value for c in self)
        elif isinstance(card_suit_or_value, Suit):
            return sum(c.suit == card_suit_or_value for c in self)
        return 0

    def __contains__(self, card_suit_or_value):
        try:
            self.index(card_suit_or_value)
            return True
        except ValueError:
            return False

    def intersect(self, other, cmp=None):
        """Compares two hands by removing cards that are not in 'other'."""
        cmp = cmp or _HAND_CMP.get()
        if cmp == HandComparison.Exact:
            return iter(set(self) & set(other))
        if cmp == HandComparison.Values:
            v1 = set(c.value for c in self)
            v2 = set(c.value for c in other)
            v12 = v1 & v2
            return (c for c in self if c.value in v12)
        if cmp == HandComparison.Suits:
            s1 = set(c.suit for c in self)
            s2 = set(c.suit for c in other)
            s12 = s1 & s2
            return (c for c in self if c.suit in s12)
        raise ValueError("cannot compare by {}".format(cmp))

    def __and__(self, other):
        return type(self)(self.intersect(other))

    def __ibitand__(self, other):
        self[:] = self.intersect(other)

    def union(self, other, cmp=None):
        """Combines two hands by adding cards from 'other'."""
        cmp = cmp or _HAND_CMP.get()
        yield from iter(self)
        if cmp == HandComparison.Exact:
            c1 = set(self)
            yield from (c for c in other if c not in c1)
        elif cmp == HandComparison.Values:
            v1 = set(c.value for c in self)
            yield from (c for c in other if c.value not in v1)
        elif cmp == HandComparison.Suits:
            s1 = set(c.suit for c in self)
            yield from (c for c in other if c.suit not in s1)
        else:
            raise ValueError("cannot compare by {}".format(cmp))

    def __or__(self, other):
        return type(self)(self.union(other))

    def __ibitor__(self, other):
        self[:] = self.union(other)

    @staticmethod
    def _default_sort_key(card):
        return card.value or 0, card.suit

    @staticmethod
    def _aces_high_sort_key(card):
        return aces_high(card.value or 0), card.suit

    @property
    def _poker_sort_key(self):
        count = {}
        for c in self:
            count[c.value] = count.get(c.value, 0) + 1
        return lambda c: (count.get(c.value), aces_high(c), c.suit)

    def sorted(self, order=None, *, reverse=False):
        """Returns a sorted list of cards in this hand."""
        order = order or _HAND_ORDER.get()
        if order == HandSort.Default:
            cards = sorted(self, key=self._default_sort_key, reverse=reverse)
        elif order == HandSort.Poker:
            cards = sorted(self, key=self._poker_sort_key, reverse=reverse)
        elif order == HandSort.AcesHigh:
            cards = sorted(self, key=self._aces_high_sort_key, reverse=reverse)
        elif order == HandSort.Unsorted:
            cards = list(self)
        else:
            raise ValueError("unable to sort with {}".format(order))
        return cards

    def sort(self, order=None, *, reverse=False):
        """Sorts the cards in this hand in place."""
        self[:] = self.sorted(order=order, reverse=reverse)

    def __format__(self, spec):
        if not spec:
            spec = "4.3"
        strs = []
        cards = self
        if spec.casefold().endswith("desc".casefold()):
            cards = self.sorted(reverse=True)
            spec = spec[:-4]
        elif spec.casefold().endswith("asc".casefold()):
            cards = self.sorted()
            spec = spec[:-3]
        return "".join(format(c, spec) for c in cards)

    def __str__(self):
        return format(self)

    def __repr__(self):
        return "<Hand({!s})>".format(super().__repr__())

    class default_comparison:
        """A context manager for overriding the default comparison.

        with Hand.default_comparison(HandComparison.Values):
            ...
        """

        def __init__(self, cmp=HandComparison.Exact):
            self._cmp = cmp
            self._token = None

        def __enter__(self):
            self._token = _HAND_CMP.set(self._cmp)
            return self

        def __exit__(self, *exc):
            _HAND_CMP.reset(self._token)

    class default_sort:
        """A context manager for overriding the default sort order.

        with Hand.default_sort(HandSort.Poker):
            ...
        """

        def __init__(self, order=HandSort.Default):
            self._order = order
            self._token = None

        def __enter__(self):
            self._token = _HAND_ORDER.set(self._order)
            return self

        def __exit__(self, *exc):
            _HAND_ORDER.reset(self._token)


collections.deck = Deck
