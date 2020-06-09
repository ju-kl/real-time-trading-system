# Real-Time Trading System

**Authors:** [Peter Eusebio](https://github.com/Pete-Best/), [Julian Kleindiek](https://github.com/ju-kl/), [Markus Wehr](https://github.com/markuswehr/)

**Date:** June 2020

GitHub repository for our final project of the 'Real-Time Intelligent Systems' course at the University of Chicago: https://github.com/ju-kl/real_time_trading_system

In this project, we built a real-time trading system that is capable of interacting with a fictitious stock market. Our trading system receives  market updates from a server and makes decisions based on the following three strategies: Correlation Strategy, Classification Strategy, and Cross-Over Strategy. The goal of each strategy is to maximize the return on the invested money. The project is structured along the following parts:

### 1. Server
- **server.py**: This script establishes a server that sequentially sends approximately 3,300 market updates to clients connected to the server in pre-defined time intervals.

### 2. Client
- **client.py**: This script establishes the client. The client represents our trading system in that it integrates and executes all of the below scripts. Once a market update is received from the server, the update will be added to the order book. The client then calls one of the different strategies to determine which action to take based on the given market update. Based on this decision, the action will be executed and reflected in the portfolio.

### 3. Order Book
- **limit_order_book.py**: The order book is able to process orders and create a bid and an ask book respectively. Each book will be a dictionary with prices as keys and order details (number of order at this price, order IDs, exchanges etc.) as items. Sorted lists are maintained which point to the dictionary, so that the best ask and bid prices available can be accessed at any time. In addition to merely adding new orders, the order book is also able to modify existing orders. If wanted, it also has the capability of executing matching orders in the bid and ask book automatically. For each stock for which orders will be coming in, a seperate order book should be initialized.

### 4. Portfolio
- **portfolio.py**: The portfolio is implemented as a class that is initialized with a cash amount and the size of any buy order. It is able to execute any transaction based on the respective action defined by the trading strategy (buy/sell/hold). It also interacts with the order book by accessing the market price to buy/sell a stock at. It will return the current cash amount and value of the portfolio every time a market update is received and the respective transaction is executed. The market value of a stock in the portfolio is defined as the average between the lowest ask and the highest bid price for a given stock.

### 5. Correlation Strategy
- **correlation_strategy.ipynb**: The purpose of this notebook is to find pairs of stocks based on the correlation of their daily returns. It outputs the correlated_stocks.csv file including the names of the stocks that have the highest correlation and are hence part of the correlation strategy. The notebook also includes data exploration necessary to code the correlation_strategy.py script.
- **correlation_strategy.py**: The correlation strategy is implemented as a class that is initialized with the pairs of stocks from the correlated_stocks.csv file. It will handle incoming market updates and return a recommended action based on the delta between the z-scores of the prices between the stock from the incoming market update and its partner symbol.

### 6. Classification Strategy
- **model_building.py**: ... @Peter
- **gbc.sav**: ... @Peter
- **classification_strategy.py**: ... @Peter

### 7. Cross-Over Strategy
- **classification_strategy.py**: ... @Peter
