from autonomic import axon, category, help, Dendrite
from datastore import Drinker, Position
from datetime import datetime
from settings import VALID_EXCHANGES
from util import Stock


@category("stockgame")
class Stockgame(Dendrite):
    def __init__(self, cortex):
        super(Stockgame, self).__init__(cortex)

    def _create_position(self, ptype):
        whom = self.lastsender

        try:
            quantity = int(self.values[0])
            symbol = self.values[1]
        except:
            self.chat("That's not right")
            return

        if quantity <= 0:
            self.chat("Do you think this is a muthafuckin game?")
            return

        stock = Stock(symbol)

        if not stock:
            self.chat("Stock not found")
            return

        if stock.exchange.upper() not in VALID_EXCHANGES:
            self.chat("Stock exchange %s DENIED!" % stock.exchange)
            return

        drinker = Drinker.objects(name=whom).first()
        if not drinker:
            drinker = Drinker(name=whom)

        cost = stock.price * quantity

        if cost > drinker.cash:
            self.chat("You is poor")
            return

        position = Position(symbol=stock.symbol,
                            price=stock.price,
                            quantity=quantity,
                            date=datetime.utcnow(),
                            type=ptype)

        drinker.positions.append(position)
        drinker.cash -= cost
        drinker.save()

        verb = 'bought' if ptype == 'long' else 'shorted'

        self.chat("%s %s %d shares of %s (%s) at %s" %\
                (whom, verb, position.quantity, stock.company,
                    position.symbol, position.price))

    def _close_position(self, ptype):
        whom = self.lastsender

        try:
            quantity = int(self.values[0])
            symbol = self.values[1]
        except:
            self.chat("That's not right")
            return

        if quantity <= 0:
            self.chat("Do you think this is a muthafuckin game?")
            return

        stock = Stock(symbol)

        if not stock:
            self.chat("Stock not found")
            return

        drinker = Drinker.objects(name=whom).first()
        if not drinker:
            self.chat("You don't have a portfolio")
            return

        check = []
        keep = []
        for p in drinker.positions:
            if p.symbol == stock.symbol and p.type == ptype:
                check.append(p)
            else:
                keep.append(p)

        if not check:
            self.chat("I don't see %s in your portfolio" % stock.symbol)
            return

        check.sort(key=lambda x: x.date)

        verb = 'sold' if ptype == 'long' else 'covered'

        for p in check:
            if quantity <= 0:
                keep.append(p)
                continue

            q = min(quantity, p.quantity)

            basis = p.price * q
            value = stock.price * q
            if ptype == 'long':
                drinker.cash += value
                net = value - basis
            else:
                net = basis - value
                drinker.cash += basis + net

            quantity -= q
            p.quantity -= q
            if p.quantity > 0:
                keep.append(p)

            self.chat("%s %s %d shares of %s at %s (net: %.02f)" % \
                    (whom, verb, q, stock.symbol, stock.price, net))

        drinker.positions = keep
        drinker.save()

    @axon
    @help("QUANTITY STOCK_SYMBOL <buy QUANTITY shares of the stock>")
    def buy(self):
        self._create_position('long')

    @axon
    @help("QUANTITY STOCK_SYMBOL <sell QUANTITY shares of the stock>")
    def sell(self):
        self._close_position('long')

    @axon
    @help("QUANTITY STOCK_SYMBOL <cover QUANTITY shares of the stock>")
    def cover(self):
        self._close_position('short')

    @axon
    @help("QUANTITY STOCK_SYMBOL <short QUANTITY shares of the stock>")
    def short(self):
        self._create_position('short')

    @axon
    @help("<show cash money>")
    def cashmoney(self):
        whom = self.lastsender
        drinker = Drinker.objects(name=whom).first()
        if not drinker:
            drinker = Drinker(name=whom)

        self.chat("You gots $%.02f" % drinker.cash)

    @axon
    @help("<show your portfolio>")
    def portfolio(self):
        whom = self.lastsender
        drinker = Drinker.objects(name=whom).first()
        if not drinker:
            self.chat("You don't exist")
            return

        if not drinker.positions:
            self.chat("You don't have one")
        else:
            drinker.positions.sort(key=lambda p: p.symbol)

            total = 0
            for p in drinker.positions:
                sign = 1 if p.type == 'long' else -1
                value = sign * p.price * p.quantity

                self.chat("%8s %10s %10d %10.02f %10.02f" % \
                        (p.type, p.symbol, p.quantity, p.price, value))

                total += value

            self.chat("%8s %10s %10s %10s %10.02f" % ('', '', '', '', total))

    @axon
    def clearstockgamepleasedontbeadickaboutthis(self):
        if self.lastsender == 'sublimnl':
            self.chat("You are why we can't have nice things.")
            return

        for drinker in Drinker.objects:
            drinker.cash = 100000
            drinker.positions = []
            drinker.save()