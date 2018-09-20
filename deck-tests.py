import unittest

from deck import Deck

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

if __name__ == '__main__':
    unittest.main()
