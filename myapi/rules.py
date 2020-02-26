# import necessary libraries
#from pymongo import MongoClient
import pandas as pd 
import datetime as dt 
#from pprint import pprint
import time
import numpy as np 
#import talib 
#import matplotlib.pyplot as plt 

# set up the connection
#client = MongoClient('catlabhome.synology.me:6017')
#db = client['hk-auto-filter']
#stock_collection = db['1211.HK_k_data']
 
# sma cross-up strategy
def getSMACrossUp(df, former='SMA10', latter='SMA20', date=dt.datetime.today().strftime("%Y-%m-%d")):
    former_sma = df[former]
    latter_sma = df[latter]
 
    rule = (former_sma > latter_sma) & (former_sma.shift() < latter_sma.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# sma cross-down strategy
def getSMACrossDown(df, former='SMA10', latter='SMA20', date=dt.datetime.today().strftime("%Y-%m-%d")):
    former_sma = df[former]
    latter_sma = df[latter]
 
    rule = (former_sma < latter_sma) & (former_sma.shift() > latter_sma.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# price cross-up sma strategy
def getPriceCrossUp(df, sma='SMA10', date=dt.datetime.today().strftime("%Y-%m-%d")):
    adj_close = df['Adj Close']
    sma = df[sma]
 
    rule = (adj_close > sma) & (adj_close.shift() < sma.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# price cross-down sma strategy
def getPriceCrossDown(df, sma='SMA10', date=dt.datetime.today().strftime("%Y-%m-%d")):
    adj_close = df['Adj Close']
    sma = df[sma]
 
    rule = (adj_close < sma) & (adj_close.shift() > sma.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# find the trigger point when RSI is above 'th_rsi'
def getRSIabove(df, th_rsi=70, date=dt.datetime.today().strftime("%Y-%m-%d")):
    rsi = df['RSI14']
 
    rule = (rsi > th_rsi) & (rsi.shift() < th_rsi)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# find the trigger point when RSI is below 'th_rsi'
def getRSIbelow(df, th_rsi=30, date=dt.datetime.today().strftime("%Y-%m-%d")):
    rsi = df['RSI']
 
    rule = (rsi < th_rsi) & (rsi.shift() > th_rsi)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# MACD cross-up strategy
def macdCrossUp(df, flag=0, date=dt.datetime.today().strftime("%Y-%m-%d")):
    # flag == 0: both macd > 0 and macd < 0
    # flag == 1: only macd > 0
    # flag == 2: only macd < 0
    macd = df['MACD']
    macdHist = df['MACDhist']
 
    if flag == 0:
        rule = (macdHist > 0) & (macdHist.shift() < 0)
    elif flag == 1:
        rule = (macdHist > 0) & (macdHist.shift() < 0) & (macd > 0)
    else:
        rule = (macdHist > 0) & (macdHist.shift() < 0) & (macd < 0)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# MACD cross-down strategy
def macdCrossDown(df, flag=0, date=dt.datetime.today().strftime("%Y-%m-%d")):
    # flag == 0: both macd > 0 and macd < 0
    # flag == 1: only macd > 0
    # flag == 2: only macd < 0
    macd = df['MACD']
    macdHist = df['MACDhist']
 
    if flag == 0:
        rule = (macdHist < 0) & (macdHist.shift() > 0)
    elif flag == 1:
        rule = (macdHist < 0) & (macdHist.shift() > 0) & (macd > 0)
    else:
        rule = (macdHist < 0) & (macdHist.shift() > 0) & (macd < 0)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# Slow %K cross-up Slow %D strategy
def slowkCrossUp(df, date=dt.datetime.today().strftime("%Y-%m-%d")):
    slowk = df['Slowk']
    slowd = df['Slowd']
 
    rule = (slowk > slowd) & (slowk.shift() < slowd.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# Slow %K cross-down Slow %D strategy
def slowkCrossDown(df, date=dt.datetime.today().strftime("%Y-%m-%d")):
    slowk = df['Slowk']
    slowd = df['Slowd']
 
    rule = (slowk < slowd) & (slowk.shift() > slowd.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# price reach the BB Upperband strategy
def getPriceAboveBBupperband(df, date=dt.datetime.today().strftime("%Y-%m-%d")):
    adj_close = df['Adj Close']
    bbupperband = df['BBupperband']
 
    rule = (adj_close > bbupperband) & (adj_close.shift() < bbupperband.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# price reach the BB Lowerband strategy
def getPriceBelowBBlowerband(df, date=dt.datetime.today().strftime("%Y-%m-%d")):
    adj_close = df['Adj Close']
    bblowerband = df['BBlowerband']
 
    rule = (adj_close < bblowerband) & (adj_close.shift() > bblowerband.shift())
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag
 
# add a new column with same value
#df['Symbol'] = '1211.HK'

"""
    Functions below are simple comparing functions not cross-up/down strategies 
"""

# price is above sma
def priceAboveSMA(df, sma='SMA10', date=dt.datetime.today().strftime("%Y-%m-%d")):
    adj_close = df['Adj Close']
    sma = df[sma]
 
    rule = (adj_close > sma)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag


# macd histogram is equal to or larger than 0
def macdHistAbove0(df, date=dt.datetime.today().strftime("%Y-%m-%d")):
    macdHist = df['MACDhist']
 
    rule = (macdHist > 0)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag


# RSI is below 'th_rsi'
# e.g. RSI < 80
def rsiBelow(df, th_rsi=80, date=dt.datetime.today().strftime("%Y-%m-%d")):
    rsi = df['RSI14']
 
    rule = (rsi < th_rsi)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag


# sma10 > sma20 
# sma10 > sma50, etc.
def smaAbove(df, former='SMA10', latter='SMA20', date=dt.datetime.today().strftime("%Y-%m-%d")):
    former_sma = df[former]
    latter_sma = df[latter]
 
    rule = (former_sma > latter_sma)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag


# Slow %K is above Slow %D 
def slowkAboveSlowd(df, date=dt.datetime.today().strftime("%Y-%m-%d")):
    slowk = df['Slowk']
    slowd = df['Slowd']
 
    rule = (slowk > slowd)
 
    results_df = df.loc[rule]
    today_result = results_df.loc[results_df['Date'] == date]
 
    if today_result.empty == False:
        b_flag = True
    else:
        b_flag = False
 
    return results_df, b_flag

    