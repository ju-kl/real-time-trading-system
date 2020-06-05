#!/usr/bin/env python
# coding: utf-8

# imports
import socket
import json
import pandas as pd
from limit_order_book import *


class Portfolio:
    # initialize
    def __init__(self, cash, order_volume):
        self.cash = cash
        self.order_volume = order_volume
        self.position = {}
        self.total = cash
        self.holdings = {}

    # book transaction assumes to receive signal ("buy", "sell", "hold") and the received_obj
    def book_transaction(self, action, received_obj, orderbooks):
        # buying
        if action == "buy":
            # TODO: check order book to see if quantity we want to purchase exists

            # check if we have enough cash to perform transaction
            if self.cash >= self.order_volume * orderbooks[received_obj['Symbol']].get_ask_book_prices()[0]:
                # update position by symbol
                if received_obj["Symbol"] in self.position:
                    self.position[received_obj["Symbol"]] += self.order_volume
                else:
                    self.position[received_obj["Symbol"]] = self.order_volume

                # update holdings by symbol
                self.holdings[received_obj["Symbol"]] = self.position[received_obj["Symbol"]] * \
                                                        orderbooks[received_obj['Symbol']].get_ask_book_prices()[0]

                # update cash
                self.cash -= self.order_volume * orderbooks[received_obj['Symbol']].get_ask_book_prices()[0]

                # update total
                #self.total = sum(self.holdings.values()) + self.cash

                # print
                print("Bought {} shares of {} at ${} per share.".format(self.order_volume, received_obj["Symbol"],
                                                                        orderbooks[received_obj['Symbol']].get_ask_book_prices()[0]))

            else:
                print("Not enough cash to execute transaction.")

        # selling
        elif (action == "sell"):
            try:
                # TODO: check order book to see if quantity we want to sell exists

                # find current position of the stock
                current_position = self.position[received_obj["Symbol"]]

                # check if we have a position
                if current_position > 0:
                    # update position by symbol; sell entire position (set position to 0)
                    self.position[received_obj["Symbol"]] = 0

                    # update holdings by symbol (will be 0 bc we sell our entire holding in the stock)
                    self.holdings[received_obj["Symbol"]] = 0

                    # update cash
                    self.cash += current_position * orderbooks[received_obj['Symbol']].get_bid_book_prices()[-1]

                    # update total
                    #self.total = sum(self.holdings.values()) + self.cash

                    # print
                    print("Sold {} shares of {} at ${} per share.".format(current_position, received_obj["Symbol"],
                                                                          orderbooks[received_obj['Symbol']].get_bid_book_prices()[-1]))

            except:
                # we don't own the stock yet and cannot sell, pass
                print("No position to sell")

        # holding
        else:
            # do nothing
            pass

        # update holdings with current market value
        try:
            # update holdings to market value of stocks owned (mean between best bid and best ask)
            self.holdings[received_obj["Symbol"]] = self.position[received_obj["Symbol"]] * \
                                                    ((orderbooks[received_obj["Symbol"]].get_bid_book_prices()[-1] +
                                                     orderbooks[received_obj['Symbol']].get_ask_book_prices()[0])/2)

            # print insight
            print("Current holdings:", self.holdings.items())

            # update total
            self.total = sum(self.holdings.values()) + self.cash

            # print insight
            print("Current cash position is:", self.cash)

        except:
            # we don't have any position of this stock yet
            pass