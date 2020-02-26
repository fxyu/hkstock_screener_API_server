import pandas as pd
import datetime as dt
from .db import *
from .rules import *
import json


def get_symbol_list_arr(db_result):
    df_symbol_list = pd.DataFrame(db_result[0])
    # sort the symbol list in ascending order
    df_symbol_list = df_symbol_list.sort_values('symbol')
    arr_symbol_list = df_symbol_list['symbol'].values

    # return an array of the whole symbol list
    return arr_symbol_list

def get_check_rule_results_all(arr_symbol_list, rule_no, start_date, end_date, check_date, b_specific_date):
    # for initialization
    b_first_stock = True

    for i_stock_no in arr_symbol_list:
        # print(i_stock_no)
        db_result = db_get_data_by_symbol(i_stock_no, start_date, end_date)

        df_list = pd.DataFrame(db_result)

        if b_first_stock == True:
            # if it is the first stock, initialize an empty dataframe for concat the results
            all_results = df_list.copy()
            all_results.drop(all_results.index, inplace=True)
            all_results['Symbol'] = []
            b_first_stock = False

        if rule_no == 0:
            # rule 0: sma cross-up strategy, SMA10 cross up SMA20
            results_df, b_flag = getSMACrossUp(df_list)
        elif rule_no == 1:
            # rule 1: sma cross-up strategy, SMA10 cross up SMA50
            results_df, b_flag = getSMACrossUp(df_list, latter='SMA50')
        elif rule_no == 2:
            # rule 2: price cross-up sma strategy, Adj Close cross up SMA10
            results_df, b_flag = getPriceCrossUp(df_list)
        elif rule_no == 3:
            # rule 3: price cross-up sma strategy, Adj Close cross up SMA20
            results_df, b_flag = getPriceCrossUp(df_list, sma='SMA20')
        elif rule_no == 4:
            # rule 4: price cross-up sma strategy, Adj Close cross up SMA50
            results_df, b_flag = getPriceCrossUp(df_list, sma='SMA50')
        elif rule_no == 5:
            # rule 5: RSI14 cross-up 30
            results_df, b_flag = getRSIabove(df_list, th_rsi=30)
        elif rule_no == 6:
            # rule 6: MACD cross-up strategy
            results_df, b_flag = macdCrossUp(df_list)
        elif rule_no == 7:
            # rule 7: Slow %K cross-up Slow %D strategy
            results_df, b_flag = slowkCrossUp(df_list)
        elif rule_no == 8:
            # rule 8: price reach the BB Lowerband strategy
            results_df, b_flag = getPriceBelowBBlowerband(df_list)
        elif rule_no == 9:
            # rule 9: sma10 > sma20
            results_df, b_flag = smaAbove(df_list)
        elif rule_no == 10:
            #   rule 10: sma10 > sma50
            results_df, b_flag = smaAbove(df_list, latter='SMA50')
        elif rule_no == 11:
            #   rule 11: sma20 > sma50
            results_df, b_flag = smaAbove(df_list, former='SMA20', latter='SMA50')
        elif rule_no == 12:
            #   rule 12: adj close > sma10
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA10')
        elif rule_no == 13:
            #   rule 13: adj close > sma20
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA20')
        elif rule_no == 14:
            #   rule 14: adj close > sma50
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA50')
        elif rule_no == 15:
            #   rule 15: adj close > sma100
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA100')
        elif rule_no == 16:
            #   rule 16: rsi < 80
            results_df, b_flag = rsiBelow(df_list, th_rsi=80)
        elif rule_no == 17:
            #   rule 17: macd hist > 0   (i.e. macd line > signal line)
            results_df, b_flag = macdHistAbove0(df_list)
        elif rule_no == 18:
            #   rule 18: slow %k > slow %d
            results_df, b_flag = slowkAboveSlowd(df_list)

        results_df['Symbol'] = i_stock_no
        if b_specific_date == True:
            results_df = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]

        # concat the results
        all_results = pd.concat([all_results, results_df], ignore_index=True)

    # rearrange the columns order 
    cols = all_results.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    all_results = all_results[cols]
    all_results['Date'] = all_results['Date'].dt.strftime('%Y-%m-%d')
    
    # convert to json format for visualization
    js_results_str = all_results.to_json(orient='records')
    js_results = json.loads(js_results_str)

    return js_results


def get_check_rule_results(stock_no, rule_no, start_date, end_date, check_date, b_specific_date):
    db_result = db_get_data_by_symbol(stock_no, start_date, end_date)

    df_list = pd.DataFrame(db_result)

    if rule_no == 0:
        # rule 0: sma cross-up strategy, SMA10 cross up SMA20
        results_df, b_flag = getSMACrossUp(df_list)
    elif rule_no == 1:
        # rule 1: sma cross-up strategy, SMA10 cross up SMA50
        results_df, b_flag = getSMACrossUp(df_list, latter='SMA50')
    elif rule_no == 2:
        # rule 2: price cross-up sma strategy, Adj Close cross up SMA10
        results_df, b_flag = getPriceCrossUp(df_list)
    elif rule_no == 3:
        # rule 3: price cross-up sma strategy, Adj Close cross up SMA20
        results_df, b_flag = getPriceCrossUp(df_list, sma='SMA20')
    elif rule_no == 4:
        # rule 4: price cross-up sma strategy, Adj Close cross up SMA50
        results_df, b_flag = getPriceCrossUp(df_list, sma='SMA50')
    elif rule_no == 5:
        # rule 5: RSI14 cross-up 30
        results_df, b_flag = getRSIabove(df_list, th_rsi=30)
    elif rule_no == 6:
        # rule 6: MACD cross-up strategy
        results_df, b_flag = macdCrossUp(df_list)
    elif rule_no == 7:
        # rule 7: Slow %K cross-up Slow %D strategy
        results_df, b_flag = slowkCrossUp(df_list)
    elif rule_no == 8:
        # rule 8: price reach the BB Lowerband strategy
        results_df, b_flag = getPriceBelowBBlowerband(df_list)
    elif rule_no == 9:
        # rule 9: sma10 > sma20
        results_df, b_flag = smaAbove(df_list)
    elif rule_no == 10:
        #   rule 10: sma10 > sma50
        results_df, b_flag = smaAbove(df_list, latter='SMA50')
    elif rule_no == 11:
        #   rule 11: sma20 > sma50
        results_df, b_flag = smaAbove(df_list, former='SMA20', latter='SMA50')
    elif rule_no == 12:
        #   rule 12: adj close > sma10
        results_df, b_flag = priceAboveSMA(df_list, sma='SMA10')
    elif rule_no == 13:
        #   rule 13: adj close > sma20
        results_df, b_flag = priceAboveSMA(df_list, sma='SMA20')
    elif rule_no == 14:
        #   rule 14: adj close > sma50
        results_df, b_flag = priceAboveSMA(df_list, sma='SMA50')
    elif rule_no == 15:
        #   rule 15: adj close > sma100
        results_df, b_flag = priceAboveSMA(df_list, sma='SMA100')
    elif rule_no == 16:
        #   rule 16: rsi < 80
        results_df, b_flag = rsiBelow(df_list, th_rsi=80)
    elif rule_no == 17:
        #   rule 17: macd hist > 0   (i.e. macd line > signal line)
        results_df, b_flag = macdHistAbove0(df_list)
    elif rule_no == 18:
        #   rule 18: slow %k > slow %d
        results_df, b_flag = slowkAboveSlowd(df_list)

    results_df['Symbol'] = stock_no
    if b_specific_date == True:
        results_df = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]

    # rearrange the columns order 
    cols = results_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    results_df = results_df[cols]
    results_df['Date'] = results_df['Date'].dt.strftime('%Y-%m-%d')
    
    # convert to json format for visualization 
    js_results_str = results_df.to_json(orient='records')
    js_results = json.loads(js_results_str)

    return js_results


def get_stock_score(stock_no, start_date, end_date):
    db_result = db_get_data_by_symbol(stock_no, start_date, end_date)

    df_list = pd.DataFrame(db_result)
    df_list['Symbol'] = stock_no
    # add a 'score' column
    df_list['Score'] = 0

    # rule 0: sma cross-up strategy, SMA10 cross up SMA20
    results_df, b_flag = getSMACrossUp(df_list)
    # update the scores and the df_list
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 1: sma cross-up strategy, SMA10 cross up SMA50
    results_df, b_flag = getSMACrossUp(df_list, latter='SMA50')
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 2: price cross-up sma strategy, Adj Close cross up SMA10
    results_df, b_flag = getPriceCrossUp(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 3: price cross-up sma strategy, Adj Close cross up SMA20
    results_df, b_flag = getPriceCrossUp(df_list, sma='SMA20')
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 4: price cross-up sma strategy, Adj Close cross up SMA50
    results_df, b_flag = getPriceCrossUp(df_list, sma='SMA50')
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 5: RSI14 cross-up 30
    results_df, b_flag = getRSIabove(df_list, th_rsi=30)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 6: MACD cross-up strategy
    results_df, b_flag = macdCrossUp(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 7: Slow %K cross-up Slow %D strategy
    results_df, b_flag = slowkCrossUp(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 8: price reach the BB Lowerband strategy
    results_df, b_flag = getPriceBelowBBlowerband(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 9: sma10 > sma20
    results_df, b_flag = smaAbove(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 10: sma10 > sma50
    results_df, b_flag = smaAbove(df_list, latter='SMA50')
    results_df['Score'] += 1
    df_list.update(results_df)
        
    # rule 11: sma20 > sma50
    results_df, b_flag = smaAbove(df_list, former='SMA20', latter='SMA50')
    results_df['Score'] += 1
    df_list.update(results_df)
        
    # rule 12: adj close > sma10
    results_df, b_flag = priceAboveSMA(df_list, sma='SMA10')
    results_df['Score'] += 1
    df_list.update(results_df)
        
    # rule 13: adj close > sma20
    results_df, b_flag = priceAboveSMA(df_list, sma='SMA20')
    results_df['Score'] += 1
    df_list.update(results_df)
        
    # rule 14: adj close > sma50
    results_df, b_flag = priceAboveSMA(df_list, sma='SMA50')
    results_df['Score'] += 1
    df_list.update(results_df)
        
    # rule 15: adj close > sma100
    results_df, b_flag = priceAboveSMA(df_list, sma='SMA100')
    results_df['Score'] += 1
    df_list.update(results_df)
        
    # rule 16: rsi < 80
    results_df, b_flag = rsiBelow(df_list, th_rsi=80)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rule 17: macd hist > 0   (i.e. macd line > signal line)
    results_df, b_flag = macdHistAbove0(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)
    
    # rule 18: slow %k > slow %d
    results_df, b_flag = slowkAboveSlowd(df_list)
    results_df['Score'] += 1
    df_list.update(results_df)

    # rearrange the columns order 
    cols = df_list.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    df_list = df_list[cols]
    df_list['Date'] = df_list['Date'].dt.strftime('%Y-%m-%d')
    

    js_results_str = df_list.to_json(orient='records')
    js_results = json.loads(js_results_str)

    return js_results


def get_start_end_dates(check_date):
    start_date = dt.datetime.strptime(check_date, "%Y%m%d") + dt.timedelta(-7)
    end_date = dt.datetime.strptime(check_date, "%Y%m%d") + dt.timedelta(+7)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')

    return start_date, end_date


def check_multiple_rules(stock_no, start_date, end_date, arr_rule_no):
    db_result = db_get_data_by_symbol(stock_no, start_date, end_date)

    df_list = pd.DataFrame(db_result)

    # for initialization
    b_first_rule = True

    for i_rule_no in arr_rule_no:
        # print(i_rule_no)
        rule_no = int(i_rule_no)

        if rule_no == 0:
            # rule 0: sma cross-up strategy, SMA10 cross up SMA20
            results_df, b_flag = getSMACrossUp(df_list)
        elif rule_no == 1:
            # rule 1: sma cross-up strategy, SMA10 cross up SMA50
            results_df, b_flag = getSMACrossUp(df_list, latter='SMA50')
        elif rule_no == 2:
            # rule 2: price cross-up sma strategy, Adj Close cross up SMA10
            results_df, b_flag = getPriceCrossUp(df_list)
        elif rule_no == 3:
            # rule 3: price cross-up sma strategy, Adj Close cross up SMA20
            results_df, b_flag = getPriceCrossUp(df_list, sma='SMA20')
        elif rule_no == 4:
            # rule 4: price cross-up sma strategy, Adj Close cross up SMA50
            results_df, b_flag = getPriceCrossUp(df_list, sma='SMA50')
        elif rule_no == 5:
            # rule 5: RSI14 cross-up 30
            results_df, b_flag = getRSIabove(df_list, th_rsi=30)
        elif rule_no == 6:
            # rule 6: MACD cross-up strategy
            results_df, b_flag = macdCrossUp(df_list)
        elif rule_no == 7:
            # rule 7: Slow %K cross-up Slow %D strategy
            results_df, b_flag = slowkCrossUp(df_list)
        elif rule_no == 8:
            # rule 8: price reach the BB Lowerband strategy
            results_df, b_flag = getPriceBelowBBlowerband(df_list)
        elif rule_no == 9:
            # rule 9: sma10 > sma20
            results_df, b_flag = smaAbove(df_list)
        elif rule_no == 10:
            #   rule 10: sma10 > sma50
            results_df, b_flag = smaAbove(df_list, latter='SMA50')
        elif rule_no == 11:
            #   rule 11: sma20 > sma50
            results_df, b_flag = smaAbove(df_list, former='SMA20', latter='SMA50')
        elif rule_no == 12:
            #   rule 12: adj close > sma10
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA10')
        elif rule_no == 13:
            #   rule 13: adj close > sma20
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA20')
        elif rule_no == 14:
            #   rule 14: adj close > sma50
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA50')
        elif rule_no == 15:
            #   rule 15: adj close > sma100
            results_df, b_flag = priceAboveSMA(df_list, sma='SMA100')
        elif rule_no == 16:
            #   rule 16: rsi < 80
            results_df, b_flag = rsiBelow(df_list, th_rsi=80)
        elif rule_no == 17:
            #   rule 17: macd hist > 0   (i.e. macd line > signal line)
            results_df, b_flag = macdHistAbove0(df_list)
        elif rule_no == 18:
            #   rule 18: slow %k > slow %d
            results_df, b_flag = slowkAboveSlowd(df_list)

        if b_first_rule == True:
            results_df['Symbol'] = stock_no
            b_first_rule = False
        
        df_list = results_df.copy()
        if df_list.empty == True:
            break

    # rearrange the columns order 
    cols = df_list.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_list = df_list[cols]
    df_list['Date'] = df_list['Date'].dt.strftime('%Y-%m-%d')
    
    # convert to json format for visualization
    js_results_str = df_list.to_json(orient='records')
    js_results = json.loads(js_results_str)

    return js_results