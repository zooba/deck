"""Implementation of the deck collection type."""

__version__ = "3.0.0"

import collections
import contextvars
import enum
import itertools
import random


_SUIT_SORT_ORDER = {
    # Handle unexpected comparisons gracefully
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
    def __init__(self, suit=None, value=None, joker=False):
        self.joker = joker
        if self.joker:
            self.suit, self.value = None, Value.Joker
        else:
            if value is None:
                suit, value = suit
            self.suit = _from_enum(Suit, suit)
            self.value = _from_enum(Value, value)
        if self.value == Value.Joker:
            self.joker = True

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
            s = s + self.suit.value
        return format(s, justify)


class Deck(collections.deque):
    def __init__(self, include_jokers=True):
        super().__init__(
            map(
                Card,
                itertools.product(
                    Suit.__members__.values(),
                    (v for v in Value.__members__.values() if v != Value.Joker),
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
    """A sort key function to sort aces high."""
    if isinstance(card, Value):
        if card is None:
            return 15
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


class HandSort(enum.Enum):
    Default = "default"
    Poker = "poker"
    Unsorted = "unsorted"


class HandComparison(enum.Enum):
    Exact = "exact"
    Values = "values"
    Suits = "suits"


_HAND_VALIDATION = contextvars.ContextVar("Hand.runtime_type_checks")
_HAND_VALIDATION.set(False)

_HAND_ORDER = contextvars.ContextVar("Hand.default_sort")
_HAND_ORDER.set(HandSort.Default)

_HAND_CMP = contextvars.ContextVar("Hand.default_comparison")
_HAND_CMP.set(HandComparison.Exact)


class Hand:
    """Represents a hand of cards.

    Used for conveniently comparing and displaying hands."""

    def __init__(self, *cards):
        self.cards = new_cards = []
        for c in cards:
            if isinstance(c, Card):
                new_cards.append(c)
            else:
                new_cards.extend(c)
        if _HAND_VALIDATION.get():
            self._check()

    def _check(self):
        invalid = [c for c in self.cards if not isinstance(c, Card)]
        if invalid:
            raise ValueError(
                "invalid objects in hand: {}".format(
                    ", ".join(repr(c) for c in invalid)
                )
            )

    def append(self, card):
        """Add a card to the hand."""
        self.cards.append(card)
        if _HAND_VALIDATION.get():
            self._check()

    def extend(self, cards):
        """Add multiple cards to the hard."""
        self.cards.extend(cards)
        if _HAND_VALIDATION.get():
            self._check()

    def index(self, card_suit_or_value):
        """Locate the first matching card, suit or value."""
        # Being passed a whole card is our fast path
        if isinstance(card_suit_or_value, Card):
            cmp = _HAND_CMP.get()
            if cmp == HandComparison.Exact:
                cards = self.cards
                for i in range(len(cards)):
                    if cards[i] == card_suit_or_value:
                        return i
                raise LookupError(card_suit_or_value)
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
            cards = self.cards
            for i in range(len(cards)):
                if cards[i].value == card_suit_or_value:
                    return i
        elif isinstance(card_suit_or_value, Suit):
            cards = self.cards
            for i in range(len(cards)):
                if cards[i].suit == card_suit_or_value:
                    return i
        raise LookupError(card_suit_or_value)

    def __contains__(self, card_suit_or_value):
        try:
            self.index(card_suit_or_value)
            return True
        except LookupError:
            return False

    def intersect(self, other, cmp=None):
        """Compares two hands by removing cards that are not in 'other'."""
        cmp = cmp or _HAND_CMP.get()
        if cmp == HandComparison.Exact:
            return iter(set(self.cards) & set(other.cards))
        if cmp == HandComparison.Values:
            v1 = set(c.value for c in self.cards)
            v2 = set(c.value for c in other.cards)
            v12 = v1 & v2
            return (c for c in self.cards if c.value in v12)
        if cmp == HandComparison.Suits:
            s1 = set(c.suit for c in self.cards)
            s2 = set(c.suit for c in other.cards)
            s12 = s1 & s2
            return (c for c in self.cards if c.suit in s12)
        raise ValueError("cannot compare by {}".format(cmp))

    def __and__(self, other):
        return type(self)(self.intersect(other))

    def __ibitand__(self, other):
        self.cards[:] = self.intersect(other)

    def union(self, other, cmp=None):
        """Combines two hands by adding cards from 'other'."""
        cmp = cmp or _HAND_CMP.get()
        yield from iter(self.cards)
        if cmp == HandComparison.Exact:
            c1 = set(self.cards)
            yield from (c for c in other.cards if c not in c1)
        elif cmp == HandComparison.Values:
            v1 = set(c.value for c in self.cards)
            yield from (c for c in other.cards if c.value not in v1)
        elif cmp == HandComparison.Suits:
            s1 = set(c.suit for c in self.cards)
            yield from (c for c in other.cards if c.suit not in s1)
        else:
            raise ValueError("cannot compare by {}".format(cmp))

    def __or__(self, other):
        return type(self)(self.union(other))

    def __ibitor__(self, other):
        self.cards[:] = self.union(other)

    @staticmethod
    def _default_sort_key(card):
        return card.value or 0, card.suit or ""

    @property
    def _poker_sort_key(self):
        count = {}
        for c in self.cards:
            count[c.value] = count.get(c.value, 0) + 1
        return lambda c: (count.get(c.value), aces_high(c), c.suit)

    def sorted(self, order=None, *, reverse=False):
        """Returns a sorted list of cards in this hand."""
        order = order or _HAND_ORDER.get()
        if order == HandSort.Default:
            cards = sorted(self.cards, key=self._default_sort_key, reverse=reverse)
        elif order == HandSort.Poker:
            cards = sorted(self.cards, key=self._poker_sort_key, reverse=reverse)
        elif order == HandSort.Unsorted:
            pass
        else:
            raise ValueError("unable to sort with {}".format(order))
        return cards

    def sort(self, order=None, *, reverse=False):
        """Sorts the cards in this hand in place."""
        order = order or _HAND_ORDER.get()
        if order == HandSort.Default:
            self.cards.sort(key=self._default_sort_key, reverse=reverse)
        elif order == HandSort.Poker:
            self.cards.sort(key=self._poker_sort_key, reverse=reverse)
        elif order == HandSort.Unsorted:
            pass
        else:
            raise ValueError("unable to sort with {}".format(order))

    def __format__(self, spec):
        import re

        if not spec:
            spec = "4.3desc"
        strs = []
        cards = self.cards
        if spec.casefold().endswith("desc".casefold()):
            cards = self.sorted(reverse=True)
            spec = spec[:-4]
        elif spec.casefold().endswith("asc".casefold()):
            cards = self.sorted()
            spec = spec[:-3]
        return "".join(format(c, spec) for c in cards)

    def __getitem__(self, index):
        return self.cards[index]

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __bool__(self):
        return bool(self.cards)

    def __str__(self):
        return format(self)

    def __repr__(self):
        return "<Hand({!r})>".format(self.cards)

    class default_comparison:
        """A context manager for overriding the default comparison."""

        def __init__(self, cmp=HandComparison.Exact):
            self._cmp = cmp
            self._token = None

        def __enter__(self):
            self._token = _HAND_CMP.set(self._cmp)
            return self

        def __exit__(self, *exc):
            _HAND_CMP.reset(self._token)

    class default_sort:
        """A context manager for overriding the default sort order."""

        def __init__(self, order=HandSort.Default):
            self._order = order
            self._token = None

        def __enter__(self):
            self._token = _HAND_ORDER.set(self._order)
            return self

        def __exit__(self, *exc):
            _HAND_ORDER.reset(self._token)

    class runtime_type_checks:
        """A context manager for enabling runtime type validation."""

        def __init__(self, check=True):
            self._check = check
            self._token = None

        def __enter__(self):
            self._token = _HAND_VALIDATION.set(self._check)
            return self

        def __exit__(self, *exc):
            _HAND_VALIDATION.reset(self._token)


collections.deck = Deck
