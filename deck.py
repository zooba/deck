'''Implementation of the deck collection type.'''

__version__ = '1.0'

import collections
import enum
import itertools
import random

class Suit(enum.Enum):
    Hearts = '♥'
    Spades = '♠'
    Clubs = '♣'
    Diamonds = '♦'

class Value(enum.IntEnum):
    Ace = 0
    One = 1
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

class Card:
    def __init__(self, suit, value=None):
        if value is None:
            self.suit, self.value = suit
        else:
            self.suit = suit
            self.value = value

    def __repr__(self):
        return f"Card({self.suit!r}, {self.value!r})"

    def __str__(self):
        return f"{self.value.value}{self.suit.value}"

class Deck(collections.deque):
    def __init__(self):
        super().__init__(map(Card, itertools.product(
            Suit.__members__.values(),
            Value.__members__.values()
        )))

    def shuffle(self, rng=random):
        rng.shuffle(self)

    deal = collections.deque.pop

    deal_from_bottom = collections.deque.popleft

collections.deck = Deck
