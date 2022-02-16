Deck
====

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

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

However, if you want to use it to write a Poker game, the `get_poker_hand` function will help.

```python
>>> from deck import Deck, get_poker_hand
>>> d = Deck(include_jokers=False)
>>> d.shuffle()
>>> p1 = [d.deal() for _ in range(5)]
>>> p2 = [d.deal() for _ in range(5)]
>>> if get_poker_hand(p1) > get_poker_hand(p2):
...     print("Player 1 wins!")
...
```
