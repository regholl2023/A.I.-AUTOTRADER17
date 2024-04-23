from alpaca.data import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
import datetime
import config
import numpy as np

client = StockHistoricalDataClient(api_key=config.KEY, secret_key=config.SECRET)

request_params = StockBarsRequest(
                        symbol_or_symbols="QQQ",
                        timeframe=TimeFrame.Day,
                        start=datetime.datetime(2024,1,1)
                 )

bars = client.get_stock_bars(request_params)

timestamp = [row[1] for row in bars.df.index]

open =bars.df['open']

low = bars.df['low']

close = bars.df['close']

high = bars.df['high']

volume = bars.df['volume']

wins = 0

position = []

profits = []

max_cash = 2000.00
#When the stock price dips 1% or lower from the days opening price BUY
#If the PL indicates a continuing dip, keep buying up to $2000 worth.
#Sell when the PL is 1% or more.

for now in range(0,len(bars.df.index)):

    #Set our average buy price (entry price)
    if len(position) > 0:
        buy_avg = np.mean(position)
    else:
        buy_avg = 0
    
    #The lowest change for the day. Which is why we use "low"
    change = round(1 - (open.iloc[now] / low.iloc[now]),5)

    #Set our profit and loss for the day
    if buy_avg > 0:
        pl = round(1 - (buy_avg / close.iloc[now]),5)
    else:
        pl = 0.0

    #Determine out entry. If change for the day dips 1% or more.
    if len(position) == 0 and change < -0.01:
        position.append(close.iloc[now])

    #Buy more if our profit and loss has dropped by 1/4%
    #But only if buying more doesn't put us over our max
    elif len(position) > 0.0 and pl < -0.0025:
        if (sum(position) + close.iloc[now]) < max_cash:
            position.append(close.iloc[now])

    #If the profit and loss on our position is 1% or more. Sell it all.
    #and track our wins and profits.
    elif pl >= 0.01:
        profits.append(close.iloc[now] - buy_avg)
        wins += 1
        position.clear()

    print(timestamp[now].date(),len(position),change, pl,wins)

#Print our our total profits.   
print(f"Profits: {sum(profits)}")