#!/usr/bin/env python
# coding: utf-8

# imports
import socket
import json
import pandas as pd
import pandas as pd
import numpy as np
from datetime import datetime
import random
from sklearn.ensemble import GradientBoostingClassifier
import pickle
import socket
import sys
import json
from correlation_strategy import *
from portfolio import *
from limit_order_book import *
import classification_strategy as cs

# initialize HOST and PORT
HOST, PORT = "127.0.0.1", 9995

## EXECUTION ##
# create socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    try:
        # connect to server
        sock.connect((HOST, PORT))

        # initialize orderbooks dict
        orderbooks = {}

        # initialize Portfolio
        portfolio = Portfolio(100000, 10)

        # initialize TradingStrategy
        #trading_strategy = CorrelationStrategy()
        trading_strategy = cs.trading_strategy_gbc()
        #trading_strategy = cs.trading_strategy_crossover()

        # initialize object counter
        counter = 0

        # receive data from server
        while True:
            print("----------------new order----------------------")
            received = str(sock.recv(1024), "utf-8").rstrip("\n")
            received_obj = json.loads(received)

            # update orderbooks
            if received_obj['Symbol'] in orderbooks.keys():
                if received_obj['Action'] == 'A':
                    orderbooks[received_obj['Symbol']].add_order_to_book(received_obj)
                else:
                    orderbooks[received_obj['Symbol']].modify_order(received_obj)
            else:
                orderbooks[received_obj['Symbol']] = Orderbook()
                if received_obj['Action'] == 'A':
                    orderbooks[received_obj['Symbol']].add_order_to_book(received_obj)
                else:
                    orderbooks[received_obj['Symbol']].modify_order(received_obj)

            # make trading decision
            action = trading_strategy.handle_market_update(received_obj)
            print(action)

            # book portfolio appropriately
            portfolio.book_transaction(action, received_obj, orderbooks)
            print("Current value of the portfolio is:", portfolio.total)

            # print counter
            print(counter)
            counter += 1

            #print("----------------ask book----------------------")
            #print(orderbooks['AAL'].get_ask_book())
            #print(orderbooks['AAL'].get_ask_book_prices())
            #print("----------------bid book----------------------")
            #print(orderbooks['AAL'].get_bid_book())
            #print(orderbooks['AAL'].get_bid_book_prices())

            # if server stops sending
            if not received:
                print("No more objects to receive from server!")
                break

    except Exception as e:
        print(e)

    finally:
        sock.close()
