import alpaca_trade_api as tradeapi
import time

#IMPORTS
############################################################################################
#FUNCTIONS

def GetStockShift(symbol, timeIncrement, timePeriod):
    # Get daily price data for AAPL over the last 5 minutes.
    barset = api.get_barset(symbol, timeIncrement, limit=timePeriod)
    aapl_bars = barset[symbol]

    # See how much AAPL moved in that timeframe.
    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    return(percent_change)

#FUNCTIONS
############################################################################################
#PROGRAM

#initialize alpaca
API_KEY = "PKUXRZ6GHDZE9VXGYO2F"
API_SECRET = "cKRe5EdTOt7pGZMJaFAeuLdFeTBTESb3JYuzkCYL"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

#only search for NASDAQ stock (just cuz theres alot of companies selling stock lol)
active_assets = api.list_assets(status='active')
nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']

#check change in price over the last 5 days of each active 
#stock available for trade through NASDAQ
i = 0
for asset in nasdaq_assets:
    if(i >=74 ):
        #keeps the bot from making too many API calls and stalling out
        print("Zzz")
        time.sleep(30)
        print("Good morning!")
        i = 0
    change = GetStockShift(asset.symbol, 'day', 5)
    if (change >= 3):
        print("sell " + asset.symbol)
    elif(change >= -3 and change < 3):
        print("hold " + asset.symbol)
    else:
        print("buy " + asset.symbol)
    i += 1
