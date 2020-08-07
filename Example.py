import alpaca_trade_api as tradeapi
import time

#IMPORTS
############################################################################################
#FUNCTIONS

#returns the percent change in price of symbol over period # of increments 
def GetPriceShift(symbol, timeIncrement, timePeriod):
    # Get daily price data for stock over the last 5 minutes.
    barset = api.get_barset(symbol, timeIncrement, limit=timePeriod)
    bars = barset[symbol]

    # See how muc stock moved in that timeframe.
    week_open = bars[0].o
    week_close = bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    return(percent_change)

#returns number of a particular asset you own
def NumberOwned(symbol):
    numOwned = 0
    for position in portfolio:
        if position.symbol == symbol:
            numOwned += 1
    return numOwned

#api call to submit a purchase order at market price
def BuyAtMarket(symbol, qty, type, tif,):
    api.submit_order(
    symbol=symbol,
    qty=qty,
    side='buy',
    type=type,
    time_in_force=tif
)

#api call to submit a sell order at market price
def SellAtMarket(symbol, qty, type, tif):
    api.submit_order(
    symbol=symbol,
    qty=qty,
    side='sell',
    type=type,
    time_in_force=tif,
)

#finds and purchases assets
def BasicBuyAlgo(count):
    i = 0
    c = 0
    for asset in nasdaq_assets:
        if c <= count:
            numOwned = NumberOwned(asset.symbol)
            if(i >=74 ):
                #keeps the bot from making too many API calls and stalling out
                time.sleep(30)
                print("still working")
                i = 0
            change = GetPriceShift(asset.symbol, 'day', 1)
            if (change <= -6):
                print("buy " + asset.symbol)
                if asset.tradable:
                    BuyAtMarket(asset.symbol, 1, 'market', 'gtc')
                    print("bought" + asset.symbol)
                #when purchase complete, make a stock object to keep track of it and its data
        i += 1
        c += 1

#search owned assets for sellable stock, then sells it
def BasicSellAlgo():
    i = 0
    for position in portfolio:
        numOwned = NumberOwned(position.symbol)
        if(i >=74 ):
            time.sleep(30)
            print("still working")
            i = 0
        change = GetPriceShift(position.symbol, 'day', 1)
        if (change >= 6):
            print("sold " + str(numOwned) + " " + position.symbol)
            SellAtMarket(position.symbol, numOwned, 'market', 'gtc')
        i += 1

#liquidate
def ClearPortfolio():
    print(len(portfolio))
    for position in portfolio:
        print(position.symbol + " " + position.qty)
        SellAtMarket(position.symbol, position.qty, 'market', 'gtc')

#FUNCTIONS
############################################################################################
#PROGRAM

#initialize alpaca
API_KEY = "PKUXRZ6GHDZE9VXGYO2F"
API_SECRET = "cKRe5EdTOt7pGZMJaFAeuLdFeTBTESb3JYuzkCYL"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

#only search for NASDAQ stock (just cuz theres alot of companies selling stock lol)
account = api.get_account()
active_assets = api.list_assets(status='active')
nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
portfolio = api.list_positions()

print("before: " + a)
print(len(portfolio))
BasicSellAlgo()
BasicBuyAlgo(20)
print("after: " + account.portfolio_value)
print(len(portfolio))

