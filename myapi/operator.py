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
    ruler = Rule()

    for idx, i_stock_no in enumerate(arr_symbol_list):

        try:
            print(idx, i_stock_no)
            db_result = db_get_data_by_symbol(i_stock_no, start_date, end_date)

            if db_result == None:
                continue

            df_list = pd.DataFrame(db_result)
            ruler.update_df(df_list)

            if b_first_stock == True:
                # if it is the first stock, initialize an empty dataframe for concat the results
                all_results = df_list.copy()
                all_results.drop(all_results.index, inplace=True)
                all_results['Symbol'] = []
                b_first_stock = False

            results_df, b_flag = ruler.run_rule(rule_no)
            

            results_df['Symbol'] = i_stock_no
            if b_specific_date == True:
                results_df = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]

            # concat the results
            all_results = pd.concat([all_results, results_df], ignore_index=True)
        except:
            import pdb; pdb.set_trace()
            break

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
    ruler = Rule(df_list)

    results_df, b_flag = ruler.run_rule(rule_no)


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

    ruler = Rule(df_list)

    for i in range(ruler.get_num_of_rules()):
        print("Rule {}:".format(i))
        results_df, b_flag = ruler.run_rule(i)
        results_df['Score'] += 1
        df_list.update(results_df)
        ruler.update_df(df_list)

    df_list = ruler.get_df()
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

    ruler = Rule(df_list)

    for i_rule_no in arr_rule_no:
        # print(i_rule_no)
        rule_no = int(i_rule_no)

        results_df, b_flag = ruler.run_rule(rule_no)

        if b_first_rule == True:
            results_df['Symbol'] = stock_no
            b_first_rule = False
        
        df_list = results_df.copy()
        if df_list.empty == True:
            break
        else:
            ruler.update_df(df_list)

    df_list = ruler.get_df()
    # rearrange the columns order 
    cols = df_list.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_list = df_list[cols]
    df_list['Date'] = df_list['Date'].dt.strftime('%Y-%m-%d')
    
    # convert to json format for visualization
    js_results_str = df_list.to_json(orient='records')
    js_results = json.loads(js_results_str)

    return js_results