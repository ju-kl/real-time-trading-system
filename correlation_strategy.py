#!/usr/bin/env python
# coding: utf-8

# imports
import pandas as pd
import numpy as np
import collections


class CorrelationStrategy:
    # initialize
    def __init__(self):
        # load symbols that are part of our strategy
        self.df_corr_top_10 = pd.read_csv("correlated_stocks.csv", index_col="Unnamed: 0")

        # initialize symbol_1_lst and symbol_2_lst
        self.symbol_1_lst = list(self.df_corr_top_10.symbol_1)
        self.symbol_2_lst = list(self.df_corr_top_10.symbol_2)

        # initialize symbols_unique
        self.symbols_unique = self.symbol_1_lst + self.symbol_2_lst

        # initialize dictionary with empty deque for each symbol in symbols_unique
        self.symbols_unique_dct = dict(zip(self.symbols_unique, [collections.deque() for i in self.symbols_unique]))

        # initialize dictionary pairs
        self.pairs = dict(zip(self.df_corr_top_10.symbol_1, self.df_corr_top_10.symbol_2))


    # function that calculates rolling z-scores by symbol
    def z_score(self, symbol):
        # slice dict by symbol
        dct = self.symbols_unique_dct[symbol]

        # find mean
        rolling_mean = np.mean(dct)

        # find std
        rolling_std = np.std(dct)

        # find z-score (price-mean)/std
        rolling_z_score = (dct[-1] - rolling_mean) / rolling_std

        # return rolling_z_score
        return rolling_z_score


    def strategy(self, received_obj, incoming_symbol, symbol_1, symbol_2):
        # append price to symbols_unique_dct
        self.symbols_unique_dct[incoming_symbol].append(float(received_obj["Price"]))

        # if we have x market updates for both symbol_1 and symbol_2 start making decisions
        if (len(self.symbols_unique_dct[symbol_1]) > 2) & (len(self.symbols_unique_dct[symbol_2]) > 2):

            # if incoming_symbol has more than x prices in deque (window for rolling averages)
            if len(self.symbols_unique_dct[incoming_symbol]) > 10:
                # pop oldest element
                self.symbols_unique_dct[incoming_symbol].popleft()

            # calculate rolling z-score of symbol_1 and symbol_2
            z_score_symbol_1 = self.z_score(symbol_1)
            z_score_symbol_2 = self.z_score(symbol_2)

            # calculate delta of z-scores
            delta = z_score_symbol_1 - z_score_symbol_2

            # if current delta > threshold: BUY symbol_2 and SELL symbol_1
            # TODO: play around with this threshold
            if delta > 1:
                action_symbol_1 = "sell"
                action_symbol_2 = "buy"
                print("buy " + symbol_2 + " and/or sell " + symbol_1)

            # if current delta < threshold: SELL symbol_2 and BUY symbol_1
            # TODO: play around with this threshold
            elif delta < -1:
                action_symbol_1 = "buy"
                action_symbol_2 = "sell"
                print("buy " + symbol_1 + " and/or sell " + symbol_2)

            # if current delta between 1.5 and -1.5: hold stocks
            # TODO: play around with this threshold
            else:
                action_symbol_1 = "hold"
                action_symbol_2 = "hold"
                #print("hold - delta between 1.5 and -1.5")

        # if no condition holds
        else:
            action_symbol_1 = "hold"
            action_symbol_2 = "hold"
            print("hold - not enough prices for rolling averages yet")

        # return
        return action_symbol_1, action_symbol_2

    # function that handles incoming market update
    def handle_market_update(self, received_obj):
        # save symbol of received_obj
        incoming_symbol = received_obj["Symbol"]

        # determine symbol_1 and symbol_2 based on incoming_symbol
        if incoming_symbol in self.symbol_1_lst:
            symbol_1 = incoming_symbol
            symbol_2 = self.pairs[incoming_symbol]
            # execute strategy
            action_symbol_1, action_symbol_2 = self.strategy(received_obj, incoming_symbol, symbol_1, symbol_2)
            # return action of incoming_symbol
            # TODO: make multiple transactions
            return action_symbol_1

        # determine symbol_1 and symbol_2 based on incoming_symbol
        elif incoming_symbol in self.symbol_2_lst:
            symbol_1 = [k for k, v in zip(self.pairs.keys(), self.pairs.values()) if v == incoming_symbol][0]
            symbol_2 = incoming_symbol
            # execute strategy
            action_symbol_1, action_symbol_2 = self.strategy(received_obj, incoming_symbol, symbol_1, symbol_2)
            # return action of incoming_symbol
            # TODO: make multiple transactions
            return action_symbol_2

        # incoming_symbol not part of our strategy
        else:
            print("hold - incoming_symbol not part of our strategy")
            return "hold"


# first stock that is bought is CTSX at 232