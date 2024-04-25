from alpaca.data import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame,TimeFrameUnit
from alpaca.data.requests import StockBarsRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest,LimitOrderRequest
from alpaca.trading.requests import TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce,OrderStatus, OrderClass
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import sys
import os
import config

symbol = "QQQ"

trading_client = TradingClient(config.KEY, config.SECRET, paper=config.paper)

def main():

##############################
########## SETUP #############
##############################

    #Availible Cash
    cash = float(trading_client.get_account().cash)
    
    #Profit/Loss Percent
    plpc = 0.0
    
    #Get our position if availible. Also set plpc if a position exists.
    try:
        position = trading_client.get_open_position(symbol)

        plpc = round(float(position.unrealized_intraday_plpc),4)
        
    except:
        position = None

    #Get stock data for the desired symbol
    stock_data = get_data(symbol)

    #Get todays stock bar. ([-1] = the last row of data returned from get_data)
    today = stock_data.iloc[-1]
   
    #Get yeterdays stock bar.
    yesterday = stock_data.iloc[-2]

    #Calculate the change so far today.
    change = round(1 - (today['open'] / today['close']),4)
   
    #Calcualte change from yeterday with current price.
    change_yesterday = round(1 - (yesterday['close'] / today['close']),4)

    #Lets log some data about this run.
    log(symbol,f"BOT Cash: {cash} PL%: {plpc} Change: {change} Change Yesterday: {change_yesterday}")






#############################
######### STRATEGY ##########
#############################

    #Lets close our position for a win and exit.
    if plpc >= 0.0105:
        close_position(symbol,plpc)
        log(symbol, f"SOLD  {plpc}")
        exit(0)

    #Lets determine if this is a first time buy. Buy if dipped 1/2% from today opening price 
    if change <= -0.005 and cash > 10.00 and position == None:
        
        buy_dollar_amnt = round((cash * 0.50),2) 
        
        buy_stock(symbol,buy_dollar_amnt)
        

    #Lets determine if this is a first time buy. Buy if dipped 1% or more from yesterday. 
    elif change_yesterday <= -0.010 and cash > 10.00 and position == None:
        
        buy_dollar_amnt = round((cash * 0.50),2) 
        
        buy_stock(symbol,buy_dollar_amnt)
        

    #If it's not a first time buy, lets determine if we want to keep addiing to our position
    elif position is not None:
        if plpc < -0.0025 and cash > 10.00:
            
            buy_dollar_amnt = round((cash * 0.10),2) 

            buy_stock(symbol,buy_dollar_amnt)
        
    
    #Do nothing. Market is flat or not moving much
    else:
        pass





#################################
######## ALPACA API WRAPS #######
#################################

#Our close position function. 
#Ultimatley calls Alpaca's close_position method
def close_position(symbol,plpc):
    log(symbol, f"Closing Position {plpc}")
    return trading_client.close_position(symbol)


#Our buy stock function. 
#Calls the Alpaca submit_order function
def buy_stock(symbol,amnt=10.00):
    market_order_data = MarketOrderRequest(
                    symbol=symbol,
                    notional=amnt,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                    )
    market_order = trading_client.submit_order(order_data=market_order_data)

    log(symbol,f"BUY {symbol} {amnt}")

    return market_order


#Our logging function. Logs info to a text file in 
#this script's folder.
def log(symbol,str):
    script_path = os.path.abspath(sys.argv[0])
    script_folder = os.path.dirname(script_path)
    with open(f'{script_folder}/{symbol}.txt', 'a') as file:
        out = f"{datetime.now()},{str}\n"
        file.write(out)

#A function to get stock data from alpaca.
#Adds a more readable timestamp.
#Returns 15 minute Pandas DataFrame

def get_data(symbol):
    my_timezone = pytz.timezone("America/New_York")

    client = StockHistoricalDataClient(api_key=config.KEY, secret_key=config.SECRET)

    request_params = StockBarsRequest(
                            symbol_or_symbols=symbol,
                            timeframe=TimeFrame.Day,
                            start= datetime.now() - timedelta(days=6)
                    )

    bars = client.get_stock_bars(request_params)    

    return bars.df


####### RUN MAIN ########
if __name__ == "__main__":
    main()