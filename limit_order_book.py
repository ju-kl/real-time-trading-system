import bisect
import pandas as pd

class Orderbook():
    def __init__(self):
        self.order_history = [] # list of orders sequenced by arrival time
        self._bid_book = {}
        self._bid_book_prices = [] # prices in ascending order and pointer to bid book
        self._bid_order_ids = [] # order ids work as a pointer to price
        self._ask_book = {}
        self._ask_book_prices = []
        self._ask_order_ids = []
        self.trade_book = [] # list of dictionaries with details for each trade
        self._order_index = 0 # unique order ids
        self.traded = False # trade occured or not

    def get_bid_book(self):
        return self._bid_book

    def get_ask_book(self):
        return self._ask_book

    def get_bid_book_prices(self):
        return self._bid_book_prices

    def get_ask_book_prices(self):
        return self._ask_book_prices

    def get_trading_book(self):
        return self.trade_book

    def get_order_history(self):
        return self.order_history

    def _add_order_to_history(self, order):
        """Add an order (dictionary) to the order_history (list)"""
        hist_order = order
        self._order_index += 1
        hist_order['exid'] = self._order_index
        self.order_history.append(hist_order)

    def add_order_to_book(self, order):
        """Use insort to maintain an ordered list of prices which serve as pointers to the orders"""
        book_order = {'OrderID': order['OrderID'],
                      'Symbol': order['Symbol'],
                      'Action': order['Action'],
                      'Exchange': order['Exchange'],
                      'Quantity': int(order['Quantity']),
                      'Price': float(order['Price']),
                      'Side': order['Side']
                      }
        if order['Side'] == 'B':
            book_prices = self._bid_book_prices
            book_ids = self._bid_order_ids
            book = self._bid_book
        else:
            book_prices = self._ask_book_prices
            book_ids = self._ask_order_ids
            book = self._ask_book
        if float(order['Price']) in book_prices:
            book[float(order['Price'])]['num_orders'] += 1
            book[float(order['Price'])]['size'] += int(order['Quantity'])
            book[float(order['Price'])]['price'] = float(order['Price'])
            book[float(order['Price'])]['order_ids'].append(order['OrderID'])
            book[float(order['Price'])]['orders'][order['OrderID']] = book_order
            if order['OrderID'] not in book_ids:
                bisect.insort(book_prices, float(order['Price']))
                book_ids.insert(book_prices.index(float(order['Price'])), order['OrderID'])
        else:
            bisect.insort(book_prices, float(order['Price']))
            book_ids.insert(book_prices.index(float(order['Price'])), order['OrderID'])
            book[float(order['Price'])] = {'num_orders': 1,
                                    'size': int(order['Quantity']),
                                    'order_ids': [order['OrderID']],
                                    'orders': {order['OrderID']: book_order}}

    def _remove_order(self, order_side, order_price, order_id):
        """Pop order_id and update order book"""
        if order_side == 'B':
            book_prices = self._bid_book_prices
            book = self._bid_book
            book_ids = self._bid_order_ids
        else:
            book_prices = self._ask_book_prices
            book = self._ask_book
            book_ids = self._ask_order_ids
        is_order = book[float(order_price)]['orders'].pop(order_id, None)
        if is_order:
            book[float(order_price)]['num_orders'] -= 1
            book[float(order_price)]['size'] -= int(is_order['Quantity'])
            book[float(order_price)]['order_ids'].remove(is_order['OrderID'])
            if book[float(order_price)]['num_orders'] == 0:
                book_prices.remove(float(order_price))
                book_ids.remove(order_id)

    def modify_order(self, order):
        """Modify order; remove older id and add modified order"""
        order_side = order['Side']
        order_quantity = int(order['Quantity'])
        order_id = order['OrderID']
        order_price = float(order['Price'])
        book = self._bid_book if order_side == 'B' else self._ask_book
        book_prices = self._bid_book_prices if order_side == 'B' else self._ask_book_prices
        book_ids = self._bid_order_ids if order_side == 'B' else self._ask_order_ids
        price_index = book_prices[book_ids.index(order_id)]
        self._remove_order(order_side, price_index, order_id)
        self.add_order_to_book(order)

    def _add_trade_to_book(self, resting_order_id, incoming_order_id, price, quantity,side):
        '''Add trades (dicts) to the trade_book list.'''
        self.trade_book.append({'resting_order_id': resting_order_id,
                                'incoming_order_id': incoming_order_id,
                                'price': price,
                                'quantity': quantity,
                                'side': side})

    def process_order(self, order):
        """Check for matching trade; if so, call _match_trade, else modify book"""
        self.traded = False
        self._add_order_to_history(order)
        if order['Action'] == 'A':
            if order['Side'] == 'B' and len(self._ask_book_prices) > 0:
                if float(order['Price']) >= self._ask_book_prices[0]:
                    self._match_trade(order)
                else:
                    self.add_order_to_book(order)
            elif order['Side'] == 'B' and len(self._ask_book_prices) == 0:
                self.add_order_to_book(order)
            elif order['Side'] == 'S' and len(self._bid_book_prices) > 0:
                if float(order['Price']) <= self._bid_book_prices[-1]:
                    self._match_trade(order)
                else:
                    self.add_order_to_book(order)
            else:
                self.add_order_to_book(order)
        else:
            self.modify_order(order)

    def _match_trade(self, order):
        """Match orders to generate trades and update books accordingly"""
        self.traded = True
        if order['Side'] == 'B':
            book_prices = self._ask_book_prices
            book_ids = self._ask_order_ids
            book = self._ask_book
            remainder = int(order['Quantity'])
            while remainder > 0:
                if book_prices:
                    price = book_prices[0]
                    if float(order['Price']) >= price:
                        book_order_id = book[price]['order_ids'][0]
                        book_order = book[price]['orders'][book_order_id]
                        if remainder >= book_order['Quantity']:
                            self._add_trade_to_book(book_order['OrderID'],
                                                    order['OrderID'],
                                                    book_order['Price'],
                                                    book_order['Quantity'],
                                                    order['Side'])
                            self._remove_order(book_order['Side'],
                                               book_order['Price'],
                                               book_order['OrderID'])
                            remainder -= book_order['Quantity']
                        else:
                            self._add_trade_to_book(book_order['OrderID'],
                                                    order['OrderID'],
                                                    book_order['Price'],
                                                    remainder,
                                                    order['Side'])
                            book_order['Quantity'] -= remainder
                            self.modify_order(book_order)
                            break
                    else:
                        order['Quantity'] = remainder
                        self.add_order_to_book(order)
                        break
                else:
                    print('Bid market collapsed for order {0}'.format(order))
                    break
