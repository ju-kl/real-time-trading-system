# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 13:43:30 2020

@author: peter
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
import pickle
import socket
import sys
import json

gbc = pickle.load(open('gbc.sav', 'rb'))

diction = {'Symbol': 'AAL', 'Description': 'American Airlines Group Inc', 'OrderID': '1101', 'Quantity': '455000', 'Action': 'A', 'Exchange': '1', 'Side': 'B', 'Price': '44.05', 'News': '0'}

collie = pd.DataFrame(columns = pd.DataFrame(diction, index = [0]).columns)

symbols = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AKAM', 'ALXN',
       'AMAT', 'AMGN', 'AMZN', 'ATVI', 'AVGO', 'BBBY', 'BIDU', 'BIIB',
       'BMRN', 'CA', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST',
       'CSCO', 'CSX', 'CTRP', 'CTSH', 'CTXS', 'DISCA', 'DISCK', 'DISH',
       'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX',
       'FOXA', 'GILD', 'GOOG', 'GOOGL', 'HSIC', 'ILMN', 'INCY', 'INTC',
       'INTU', 'ISRG']

company_window = {}

for i in range(len(symbols)):
    company_window[symbols[i]] = collie

class trading_strategy_gbc:
    
    def __init__(self):
        self.company_window = company_window.copy()


    def predict_ten(self, dfo):

        # takes dfo of at least 10 rows
        df = dfo.reset_index().drop('index', axis=1).copy()
        df['Quantity'] = pd.to_numeric(df['Quantity'])
        df['Exchange'] = pd.to_numeric(df['Exchange'])
        df['Price'] = pd.to_numeric(df['Price'])
        df['News'] = pd.to_numeric(df['News'])

        model = gbc

        short = 5
        long = 10

        df['Action A'] = df['Action'].str.replace('A', '1').str.replace('M', '0')
        df['Side B'] = df['Side'].str.replace('B', '1').str.replace('S', '0')
        df['Exchange 1'] = df['Exchange'].replace([1, 2, 3], [1, 0, 0])
        df['Exchange 2'] = df['Exchange'].replace([1, 2, 3], [0, 1, 0])

        df['Quantity_short_mavg'] = df['Quantity'].rolling(window=short, min_periods=short).mean()
        df['Price_short_mavg'] = df['Price'].rolling(window=short, min_periods=short).mean()
        df['News_short_mavg'] = df['News'].rolling(window=short, min_periods=short).mean()

        df['Quantity_long_mavg'] = df['Quantity'].rolling(window=long, min_periods=long).mean()
        df['Price_long_mavg'] = df['Price'].rolling(window=long, min_periods=long).mean()
        df['News_long_mavg'] = df['News'].rolling(window=long, min_periods=long).mean()

        df['Quantity_short_std'] = df['Quantity'].rolling(window=short, min_periods=short).std()
        df['Price_short_std'] = df['Price'].rolling(window=short, min_periods=short).std()
        df['News_short_std'] = df['News'].rolling(window=short, min_periods=short).std()

        df['Quantity_long_std'] = df['Quantity'].rolling(window=long, min_periods=long).std()
        df['Price_long_std'] = df['Price'].rolling(window=long, min_periods=long).std()
        df['News_long_std'] = df['News'].rolling(window=long, min_periods=long).std()

        df['Quantity_short_diff'] = df['Quantity'].diff(periods=short - 1)
        df['Price_short_diff'] = df['Price'].diff(periods=short - 1)
        df['News_short_diff'] = df['News'].diff(periods=short - 1)

        df['Quantity_long_diff'] = df['Quantity'].diff(periods=long - 1)
        df['Price_long_diff'] = df['Price'].diff(periods=long - 1)
        df['News_long_diff'] = df['News'].diff(periods=long - 1)

        one_x = pd.DataFrame(df.iloc[len(df) - 1]).transpose()
        one_x = one_x.drop(['Symbol', 'Description', 'OrderID', 'Action', 'Exchange', 'Side'], axis=1)
        current = pd.DataFrame(dfo.iloc[len(dfo) - 1]).transpose()

        if model.predict(one_x) == 0:
            current['Response'] = 'buy'
        elif model.predict(one_x) == 1:
            current['Response'] = 'hold'
        elif model.predict(one_x) == 2:
            current['Response'] = 'sell'
        else:
            current['Response'] = 'NaN'

        return current

    def handle_market_update(self, received_obj):
        print(self.company_window[received_obj['Symbol']])
        receive_frame = pd.DataFrame(received_obj, index = [i])
        self.company_window[received_obj['Symbol']] = self.company_window[received_obj['Symbol']].append(receive_frame)
        if len(self.company_window[received_obj['Symbol']]) < 11:
            print(len(self.company_window[received_obj['Symbol']]))
            receive_frame['Response'] = 'hold'
        elif len(self.company_window[received_obj['Symbol']]) == 11:
            receive_frame = self.predict_ten(self.company_window[received_obj['Symbol']])
        elif len(self.company_window[received_obj['Symbol']]) > 11:
            self.company_window[received_obj['Symbol']] = self.company_window[received_obj['Symbol']].iloc[-11:]
            receive_frame = self.predict_ten(self.company_window[received_obj['Symbol']])
        return receive_frame['Response'].iloc[0]

    # first trades at 561

    
class trading_strategy_crossover:
    
    def __init__(self):
        self.company_window = company_window.copy()

    def crossover(self, dfo):

        # takes dfo of at least 10 rows

        df = dfo.reset_index().drop('index', axis=1).copy()
        df['Quantity'] = pd.to_numeric(df['Quantity'])
        df['Exchange'] = pd.to_numeric(df['Exchange'])
        df['Price'] = pd.to_numeric(df['Price'])
        df['News'] = pd.to_numeric(df['News'])

        short = 5
        long = 10

        df['Price_short_mavg'] = df['Price'].rolling(window=short, min_periods=short).mean()
        df['Price_long_mavg'] = df['Price'].rolling(window=long, min_periods=long).mean()
        df['short_minus_long'] = df['Price_short_mavg'] - df['Price_long_mavg']

        current = pd.DataFrame(df.iloc[len(dfo) - 1]).transpose()

        if current['short_minus_long'].iloc[0] > .05:
            current['Response'] = 'buy'
        elif (current['short_minus_long'].iloc[0] <= .05) & (current['short_minus_long'].iloc[0] >= -.05):
            current['Response'] = 'hold'
        elif current['short_minus_long'].iloc[0] < -.05:
            current['Response'] = 'sell'
        else:
            current['Response'] = 'NaN'

        return current


    def handle_market_update(self, received_obj):
        receive_frame = pd.DataFrame(received_obj, index = [i])
        self.company_window[received_obj['Symbol']] = self.company_window[received_obj['Symbol']].append(receive_frame)
        if len(self.company_window[received_obj['Symbol']]) < 11:
            receive_frame['Response'] = 'hold'
        elif len(self.company_window[received_obj['Symbol']]) == 11:
            receive_frame = self.crossover(self.company_window[received_obj['Symbol']])
        elif len(self.company_window[received_obj['Symbol']]) > 11:
            self.company_window[received_obj['Symbol']] = self.company_window[received_obj['Symbol']].iloc[-11:]
            receive_frame = self.crossover(self.company_window[received_obj['Symbol']])
        return receive_frame['Response'].iloc[0]

    # this should be starting to trade around 600