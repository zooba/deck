'''Implementation of the deck collection type.'''

__version__ = '2.1'

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

class Card:
    def __init__(self, suit=None, value=None, joker=False):
        self.joker = joker
        if self.joker:
            self.suit, self.value = None, None
        else:
            if value is None:
                self.suit, self.value = suit
            else:
                self.suit = suit
                self.value = value

    def __repr__(self):
        return "Card(joker=True)" if self.joker else f"Card({self.suit!r}, {self.value!r})"

    def __str__(self):
        return "Joker" if self.joker else f"{self.value.value}{self.suit.value}"

class Deck(collections.deque):
    def __init__(self, include_jokers=True):
        super().__init__(map(Card, itertools.product(
            Suit.__members__.values(),
            Value.__members__.values()
        )))
        if include_jokers:
            self.append(Card(joker=True))
            self.append(Card(joker=True))

    def shuffle(self, rng=random):
        rng.shuffle(self)

    deal = collections.deque.pop

    deal_from_bottom = collections.deque.popleft

collections.deck = Deck

if __name__ == '__main__':
    # Basic tests

    d = Deck()
    assert len(d) == 54

    d = Deck(include_jokers=False)
    assert len(d) == 52
