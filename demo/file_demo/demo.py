import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck(object):

    # ２－１０，ＪＱＫＡ
    ranks = [str(n) for n in range(2,11)] + list('JQKA')

    # 花色
    suits = 'spades dismonds clubs hearts'.split()

    def __init__(self):
        # 通过for循环　拿到所有的
        self._cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]


    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

# beer_card = Card('7', 'diamonds')
# print(beer_card)
#
f = FrenchDeck()
print(f.__len__())

