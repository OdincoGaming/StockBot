import alpaca_trade_api as tradeapi
import time

#IMPORTS
############################################################################################
#FUNCTIONS

def GetPriceShift(symbol, timeIncrement, timePeriod):
    # Get daily price data for stock over the last 5 minutes.
    barset = api.get_barset(symbol, timeIncrement, limit=timePeriod)
    bars = barset[symbol]

    # See how muc stock moved in that timeframe.
    week_open = bars[0].o
    week_close = bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    return(percent_change)

def NumberOwned(symbol):
    numOwned = 0
    for position in portfolio:
        if position.symbol == symbol:
            numOwned += 1
    return numOwned

def BuyAtMarket(symbol, qty, type, tif,):
    api.submit_order(
    symbol=symbol,
    qty=qty,
    side='buy',
    type=type,
    time_in_force=tif
)

def SellAtMarket(symbol, qty, type, tif):
    api.submit_order(
    symbol=symbol,
    qty=qty,
    side='sell',
    type=type,
    time_in_force=tif,
)

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
portfolio = api.list_positions()

#check change in price over the last 5 days of each active 
#stock available for trade through NASDAQ
i = 0
for asset in nasdaq_assets:
    numOwned = NumberOwned(asset.symbol)
    if(i >=74 ):
        #keeps the bot from making too many API calls and stalling out
        print("Zzz")
        time.sleep(30)
        print("Good morning!")
        i = 0
    change = GetPriceShift(asset.symbol, 'day', 5)
    if (change >= 3):
        print("sell " + asset.symbol)
        if numOwned >= 1:
            if asset.tradable:
                SellAtMarket(asset.symbol, 1, 'market', 'gtc')
    elif(change >= -3 and change < 3):
        print("hold " + asset.symbol)
        #update how many times held on stock object
    else:
        print("buy " + asset.symbol)
        if asset.tradable:
            BuyAtMarket(asset.symbol, 1, 'market', 'gtc')
        #when purchase complete, make a stock object to keep track of it and its data
        i += 1
