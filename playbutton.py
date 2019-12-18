import alpaca_trade_api as tradeapi
import time
import csv
import random
import os
import csv_to_dataset
#IMPORTS
############################################################################################
#EXAMPLE

def GetStockShift(symbol, timeIncrement, timePeriod):
    barset = api.get_barset(symbol, timeIncrement, limit=timePeriod)
    bars = barset[symbol]
    print(bars)

    week_open = bars[0].o
    week_close = bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    return(percent_change)

#EXAMPLE
############################################################################################
#PROGRAM

#initialize alpaca
API_KEY = "PKUXRZ6GHDZE9VXGYO2F"
API_SECRET = "cKRe5EdTOt7pGZMJaFAeuLdFeTBTESb3JYuzkCYL"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

active_assets = api.list_assets(status='active')
nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']

####################################################################################
#get data on symbol
def GetData(symbol):
    limit = 1000

    #a list with a list which is a lists of lists (I assume you can send in multiple symbols at once to get a list of lists that are lists of lists)
    barset = api.get_barset(symbol, 'day', limit=limit)

    #top level list in barset
    bars = barset[symbol]

    filename = symbol + '.csv'
    path = os.getcwd() + "\\data\\csv\\" + filename

    try:
        with open(path, 'w+', newline='') as file:
            i = 0
            fieldnames = ['date', '1. open', '2. high', '3. low', '4. close', '5. volume']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            while i < limit:
                t = bars[i].t
                o = bars[i].o
                h = bars[i].h
                l = bars[i].l
                c = bars[i].c
                v = bars[i].v
                writer.writerow({'date':t,'1. open':o,'2. high':h,'3. low':l,'4. close':c,'5. volume':v})
                i += 1
    except:
        print("not enough data for " + symbol)
####################################################################################
i = 0
c = 0
count = 99
usableList = []

#for asset in nasdaq_assets:
#    if c < count:
#        if i > 49:
#            time.sleep(20)
#            i = 0
#        GetData(asset.symbol)
#    i += 1
#    c += 1

#have to make sure the API returned enough information, not all stocks have 20 years worth of data
path = os.getcwd() + "\\data\\csv"  
for csv_file_path in list(filter(lambda x: x.endswith('.csv'), os.listdir(path))):

    filepath = path + "\\" + csv_file_path
    with open(filepath,"r") as f:

        reader = csv.reader(f,delimiter = ",")
        data = list(reader)
        #row count - 1 = # of rows filled with data from alpaca
        row_count = len(data)
        if row_count >= 1000:
            usableList.append(csv_file_path)

####################################################################################
for item in usableList:
    csv_to_dataset.csv_to_model(item)