# Deck

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Deck is an implementation of the `deck` collection type, commonly confused with [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque).

```python
>>> from deck import Deck
>>> d = Deck()
>>> d.shuffle()
>>> d.deal()
Card(<Suit.Diamonds: '♦'>, <Value.Two: 2>)
>>> d.deal()
Card(<Suit.Diamonds: '♦'>, <Value.Three: 3>)
>>> d.deal()
Card(<Suit.Hearts: '♥'>, <Value.Ten: 10>)
>>> d.deal()
Card(<Suit.Diamonds: '♦'>, <Value.Nine: 9>)
```

Deck supports cheating, if that's how you want to play.

```python
>>> d.deal_from_bottom()
Card(<Suit.Spades: '♠'>, <Value.Five: 5>)
```

Importing the `deck` module also globally corrects other typographical errors that may occur in your code.

```python
>>> import deck
>>> from collections import deck
>>> deck
<class 'deck.Deck'>
```

**Taking this module too seriously would be a mistake.**

# API

Despite its origins as a bit of a joke, this module does provide some useful building blocks for card games.

## Deck

The `Deck` class is, in fact, a subclass of [`deque`](https://docs.python.org/library/collections.html#collections.deque), and has default contents of 54 `Card` instances representing a standard deck of cards, including jokers. To omit jokers, pass `include_jokers=False` when initialising.

```python
>>> from deck import Deck
>>> deck = Deck(include_jokers=False)
>>> if not any(card.joker for card in deck):
...     print("No jokers here!")
...
No jokers here!
```

Decks may be shuffled using the `shuffle` method, which optionally takes a `random` parameter to override the default `random` module.

```python
>>> from random import Random
>>> r = Random(100)
>>> deck.shuffle(r)
>>> deck.deal()
Card(<Suit.Hearts: '♥'>, <Value.Ten: 10>)
```

The standard `pop` and `popleft` methods are aliased as `deal` and `deal_from_bottom`. All other `deque` methods are available, however no validation is performed to stop you adding whatever you like into the deck.

```python
>>> deck.appendleft("not a card")
>>> deck.deal_from_bottom()
'not a card'
```

The `Hand` object is a convenient way to handle collections of cards, and the `Deck.deal_hands` method is the easiest way to create them.

```python
>>> deck.deal_hands(hands=2, cards=2)
[
    <Hand([
        Card(<Suit.Clubs: '♣'>, <Value.Four: 4>),
        Card(<Suit.Hearts: '♥'>, <Value.Queen: 12>)
    ])>,
    <Hand([
        Card(<Suit.Diamonds: '♦'>, <Value.Queen: 12>),
        Card(<Suit.Diamonds: '♦'>, <Value.Seven: 7>)
    ])>
]
```

## Hand

A `Hand` object is actually just a `list` containing cards, and all traditional `list` methods are available. Some additional methods are provided for ease of use as a hand of cards, and some are overridden for similar reasons.

Hands can be directly instantiated just like a list. No type checking is performed at this stage, however, you can call the `check_contents` method explicitly to verify that all elements are Card objects.

```python
>>> card1 = deck.deal()
>>> cards = [deck.deal(), deck.deal(), deck.deal()]
>>> hand = Hand([card1, *cards])
>>> hand.check_contents()
>>> hand.append('not a card')
>>> hand.check_contents()
ValueError: invalid objects in hand: 'not a card'
```

The `index` method is overridden to allow finding cards with either a card object, a value, a suit, or a string or int that represents one of these. Similarly, the `in` operator will also accept these values.

```python
>>> deck = Deck()
>>> deck.shuffle(random=Random(101))
>>> hand = deck.deal_hands(hands=1, cards=10)[0]
>>> 9 in hand
True
>>> "diamonds" in hand
True
>>> hand.index(Card(Suit.Diamonds, Value.Nine))
ValueError: Card(<Suit.Diamonds: '♦'>, <Value.Nine: 9>) is not in list
>>> hand.index(Suit.Diamonds)
6
>>> hand.index("diamonds")
6
>>> hand.index(Value.Nine)
2
```

`intersect` and `union` methods are added to allow combining two hands (more precisely, a Hand with an iterable of Cards). They return lazy iterables that will yield the new set of cards, potentially reordered from the original hand.

Intersection returns all cards from the original hand (`self`) that match cards in the comparator (`other`).

Union returns all cards from the original hand (`self`), and also those from the other that _do not_ match cards in the original.

Whether cards are considered to match depends on the `cmp` argument (a value from the `HandComparison` enum) or the current default comparison. Note that these operations are sensitive to the order of arguments, and should be considered

The bitwise operators `|`, `|=` and `&`, `&=` are likewise enhanced for these operations, and result in a new `Hand` instance or an in-place update. The default comparison method is always used.

```python
>>> hand1 = Hand([Card(Suit.Diamonds, Value.Nine), Card(Suit.Spades, Value.Queen)])
>>> hand2 = Hand([Card(Suit.Diamonds, Value.Nine), Card(Suit.Hearts, Value.Queen)])
>>> hand1.intersect(hand2)
<iterator object at 0x...>
>>> str(Hand(hand1.intersect(hand2)))
'9♦  '
>>> str(Hand(hand1.union(hand2)))
'Q♠  Q♥  9♦  '
>>> str(hand1 | hand2)
'Q♠  Q♥  9♦  '
>>> with Hand.default_comparison(HandComparison.Values):
...     str(hand1 | hand2)
...
'Q♠  9♦  '
>>> with Hand.default_comparison(HandComparison.Suits):
...     str(hand1 & hand2)
...
'9♦  '
```

Hands may be sorted, either in place or by returning a new iterable. Note that the built-in `sorted` function may not behave appropriately, and the `sorted` method should be preferred.

Ordering may be selected between `HandSort.Default` (cards in numeric, then suit, order), `HandSort.AcesHigh` (same but aces are highest, not lowest), or `HandSort.Poker` (quads/triples/pairs sort highest, then by numeric and suit order). Suits sort according to bridge rankings.

The default ordering may be overridden for the active context by entering the `Hand.default_sort` context manager. This is the only way to affect the sort order used by the 'asc' or 'desc' format specifier.

```python
>>> deck = Deck()
>>> deck.shuffle(random=Random(101))
>>> hand1, hand2 = deck.deal_hands(hands=2, cards=5)
>>> str(hand1)
'Q♣  9♣  4♣  4♦  A♠  '
>>> hand1.sort()
>>> str(hand1)
'A♠  4♣  4♦  9♣  Q♣  '
>>> str(Hand(hand1.sorted(HandSort.Poker, reverse=True)))
'4♦  4♣  A♠  Q♣  9♣  '
>>> with Hand.default_sort(HandSort.AcesHigh):
...     print(f'{hand1:5.3desc}')
...
A♠   Q♣   9♣   4♦   4♣
```

## get_poker_hand

The `get_poker_hand` function takes an iterable of cards and calculates the best available poker hand. If more than five cards are provided, all combinations of five are checked.

The result of the function is a tuple containing first a `PokerHand` value, followed by the relevant values of cards in the hand for determining a winner. The number of elements varies, but tuples can always be compared to determine the stronger hand. Stronger hands compare _greater_ than others.

Suits are not taken into account for breaking ties.

```python
>>> from deck import Deck, get_poker_hand
>>> deck = Deck(include_jokers=False)
>>> deck.shuffle()
>>> p1, p2 = deck.deal_hands(hands=2, cards=5)
>>> with Hand.default_sort(HandSort.Poker):
...     print(f'Player 1: {p1:>6.5desc}')
...     print(f'Player 2: {p2:>6.5desc}')
...
Player 1:     6♦    6♣  Ace♦    9♣    8♦
Player 2:     4♠    4♦  Que♠    7♠    5♠
>>> if get_poker_hand(p1) > get_poker_hand(p2):
...     print("Player 1 wins!")
...
Player 1 wins!
```
