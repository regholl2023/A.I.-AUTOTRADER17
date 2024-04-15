from alpaca.data import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
import datetime


ENDPOINT = 'https://paper-api.alpaca.markets'
KEY = ''
SECRET = ''
paper=True


client = StockHistoricalDataClient(api_key=KEY, secret_key=SECRET)

request_params = StockBarsRequest(
                        symbol_or_symbols="QQQ",
                        timeframe=TimeFrame.Hour,
                        start=datetime.datetime(2024,1,1)
                 )

bars = client.get_stock_bars(request_params)


#print(bards.df.colums)

#print(bars.df.head)

timestamp = [row[1] for row in bars.df.index]
close = bars.df['close']
volume = bars.df['volume']

for now in range(0,len(bars.df.index)):

    close_diff = close[now] - close[now - 5]
    # Print the timestamp, the closing proce and the
    # difference in closing price from 5 bars ago
    print(timestamp[now],close[now],close_diff)
    
