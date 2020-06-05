# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 20:25:57 2020

@author: peter
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random
from sklearn.ensemble import GradientBoostingClassifier
import pickle

df = pd.read_csv('./finance/finance.csv')

def extract(df,symbol):
    
    df = df[df['Symbol'] == symbol].copy()
    
    short = 5
    long = 10
    
    df['Change'] = -df['Price'].pct_change(periods = -1)
    
    df['Buy'] = (df['Price'].pct_change(periods = -1) < -.05).astype('int')
    df['Hold'] = (np.logical_and((df['Price'].pct_change(periods = -1)) >= -.05, ((df['Price'].pct_change(periods = -1))) <= .05)).astype('int')
    df['Sell'] = (df['Price'].pct_change(periods = -1) > .05).astype('int')
    
    df['Response'] = df['Hold'] + df['Sell']*2  #buy = 0, hold = 1, sell = 2
    
    df['Action A'] = df['Action'].str.replace('A','1').str.replace('M','0')
    df['Side B'] = df['Side'].str.replace('B','1').str.replace('S','0')
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
    
    df['Quantity_short_diff'] = df['Quantity'].diff(periods = short-1)
    df['Price_short_diff'] = df['Price'].diff(periods = short-1)
    df['News_short_diff'] = df['News'].diff(periods = short-1)
    
    df['Quantity_long_diff'] = df['Quantity'].diff(periods = long-1)
    df['Price_long_diff'] = df['Price'].diff(periods = long-1)
    df['News_long_diff'] = df['News'].diff(periods = long-1)
    
    return df

symbols = df.Symbol.unique()
indy = extract(df,'AAL').columns
new = pd.DataFrame(columns = indy)

for i in range(len(symbols)):
    new = new.append(extract(df,symbols[i]))

data = new.dropna(axis = 0)

use = data.drop(['Symbol','Description','OrderID','Action','Exchange','Side'],axis = 1)

X = use.drop(['Change','Buy','Hold','Sell','Response'],axis = 1)
y = np.array(use['Response'].astype('int'))

gbc = GradientBoostingClassifier(random_state = 0, n_estimators = 400, learning_rate = .1, max_depth = 5)
gbc.fit(X, y)

pickle.dump(gbc, open('gbc.sav', 'wb'))