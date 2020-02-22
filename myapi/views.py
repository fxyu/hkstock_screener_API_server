from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from pymongo import MongoClient
from .db import DBClient as db
from .db import *
import pandas as pd
import datetime as dt
from pprint import pprint

import pickle
import base64
import sys
import json

from .rules import getSMACrossUp, getPriceCrossUp

# Create your views here.
@api_view(['GET',])
def api_stock_data_all(request, stock_no, start_date, end_date):
    try:
        # Get the data from database
        db_result = db_get_data_by_symbol(stock_no,start_date,end_date)
        if request.method == "GET":
            return Response(db_result)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET',])
def api_get_all_symbol(request):
    try:
        df_list = db_get_all_symbol()
        if request.method == "GET":
            return Response(df_list)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule_all(request, rule_no, start_date, end_date):
    try:
        # Get the symbol list from database
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$group":{
                    "_id": {"symbol" : "$symbol"},
                    "symbol": {"$first" : "$symbol"}}
            },
            {"$group":{
                    "_id": "null",
                    "symbol": {"$push" : "$symbol"}}
            },
            {"$project":{"_id" : 0}},
        ])

        #df_stock_list = list(db_result)
        df_stock_list = pd.DataFrame(list(db_result)[0])
        df_stock_list = df_stock_list.sort_values('symbol')
        arr_stock_list = df_stock_list['symbol'].values

        bFirstStock = True
        # for demo, the first 20 stocks, otherwise, it is too slow.
        for i_stock_no in arr_stock_list[0:20]:
            #print(i_stock_no)
            db_result = stock_collection.aggregate([
                {"$match": {"symbol":i_stock_no}},
                {"$match": {"k_data.Date" : { 
                            "$gt": dt.datetime.strptime(start_date, "%Y%m%d"), 
                            "$lt": dt.datetime.strptime(end_date, "%Y%m%d")
                        }}
                },
                {"$project":{ "k_data": {"$filter": {
                    "input": '$k_data',
                    "as": 'kdata',
                    "cond": {"$and": [{"$gt": ['$$kdata.Date', dt.datetime.strptime(start_date, "%Y%m%d")]},
                                    {"$lt": ['$$kdata.Date', dt.datetime.strptime(end_date, "%Y%m%d")]}
                            ]}}},
                    "_id": 0
                }},
                {"$unwind": "$k_data"},
                {"$sort" : {  "k_data.Date" : 1  }  },
                {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
                {"$project": {"k_data": 1, "_id": 0}},
                ])

            # dataframe of a particular stock
            df = list(db_result)
            if df:
                df_list = pd.DataFrame(df[0]['k_data'])
                if bFirstStock == True:
                    all_results = df_list.copy()
                    all_results.drop(all_results.index, inplace=True)
                    all_results['Symbol'] = []
                    bFirstStock = False

                if rule_no == 0:
                    # rule 0: sma cross-up strategy, SMA10 cross up SMA20
                    results_df, b_flag = getSMACrossUp(df_list)
                    results_df['Symbol'] = i_stock_no
                elif rule_no == 1:
                    # rule 1: price cross-up sma strategy, Adj Close cross up SMA10
                    results_df, b_flag = getPriceCrossUp(df_list)
                    results_df['Symbol'] = i_stock_no



                all_results = pd.concat([all_results, results_df], ignore_index=True)

        # rearrange the columns order
        cols = all_results.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        all_results = all_results[cols]
        all_results['Date'] = all_results['Date'].dt.strftime('%Y-%m-%d')


        js_results_str = all_results.to_json(orient='records')
        js_results = json.loads(js_results_str)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET',])
def api_check_rule(request, stock_no, rule_no, start_date, end_date):
    try:
        # Get stock data from database
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$match": {"symbol":stock_no}},
            {"$match": {"k_data.Date" : { 
                        "$gt": dt.datetime.strptime(start_date, "%Y%m%d"), 
                        "$lt": dt.datetime.strptime(end_date, "%Y%m%d")
                    }}
            },
            {"$project":{ "k_data": {"$filter": {
                "input": '$k_data',
                "as": 'kdata',
                "cond": {"$and": [{"$gt": ['$$kdata.Date', dt.datetime.strptime(start_date, "%Y%m%d")]},
                                {"$lt": ['$$kdata.Date', dt.datetime.strptime(end_date, "%Y%m%d")]}
                        ]}}},
                "_id": 0
            }},
            {"$unwind": "$k_data"},
            {"$sort" : {  "k_data.Date" : 1  }  },
            {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
            {"$project": {"k_data": 1, "_id": 0}},
            ])

        # dataframe of a particular stock
        df = list(db_result)
        if df:
            df_list = pd.DataFrame(df[0]['k_data'])

            if rule_no == 0:
                # rule 0: sma cross-up strategy, SMA10 cross up SMA20
                results_df, b_flag = getSMACrossUp(df_list)
                results_df['Symbol'] = stock_no
            elif rule_no == 1:
                # rule 1: price cross-up sma strategy, Adj Close cross up SMA10
                results_df, b_flag = getPriceCrossUp(df_list)
                results_df['Symbol'] = stock_no


        # rearrange the columns order
        cols = results_df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        results_df = results_df[cols]
        results_df['Date'] = results_df['Date'].dt.strftime('%Y-%m-%d')


        js_results_str = results_df.to_json(orient='records')
        js_results = json.loads(js_results_str)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule_on_date_all(request, rule_no, check_date):
    try:
        start_date = dt.datetime.strptime(check_date, "%Y%m%d") + dt.timedelta(-7)
        end_date = dt.datetime.strptime(check_date, "%Y%m%d") + dt.timedelta(+7)

        # Get the symbol list from database
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$group":{
                    "_id": {"symbol" : "$symbol"},
                    "symbol": {"$first" : "$symbol"}}
            },
            {"$group":{
                    "_id": "null",
                    "symbol": {"$push" : "$symbol"}}
            },
            {"$project":{"_id" : 0}},
        ])

        #df_stock_list = list(db_result)
        df_stock_list = pd.DataFrame(list(db_result)[0])
        df_stock_list = df_stock_list.sort_values('symbol')
        arr_stock_list = df_stock_list['symbol'].values

        bFirstStock = True
        # for demo, the first 100 stocks, otherwise, it is too slow.
        for i_stock_no in arr_stock_list[0:100]:
            #print(i_stock_no)
            db_result = stock_collection.aggregate([
                {"$match": {"symbol":i_stock_no}},
                {"$match": {"k_data.Date" : { 
                            "$gt": start_date, 
                            "$lt": end_date
                        }}
                },
                {"$project":{ "k_data": {"$filter": {
                    "input": '$k_data',
                    "as": 'kdata',
                    "cond": {"$and": [{"$gt": ['$$kdata.Date', start_date]},
                                    {"$lt": ['$$kdata.Date', end_date]}
                            ]}}},
                    "_id": 0
                }},
                {"$unwind": "$k_data"},
                {"$sort" : {  "k_data.Date" : 1  }  },
                {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
                {"$project": {"k_data": 1, "_id": 0}},
                ])

            # dataframe of a particular stock
            df = list(db_result)
            if df:
                df_list = pd.DataFrame(df[0]['k_data'])
                if bFirstStock == True:
                    all_results = df_list.copy()
                    all_results.drop(all_results.index, inplace=True)
                    all_results['Symbol'] = []
                    bFirstStock = False

                if rule_no == 0:
                    # rule 0: sma cross-up strategy, SMA10 cross up SMA20
                    results_df, b_flag = getSMACrossUp(df_list)
                    results_df['Symbol'] = i_stock_no
                    date_result = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]
                elif rule_no == 1:
                    # rule 1: price cross-up sma strategy, Adj Close cross up SMA10
                    results_df, b_flag = getPriceCrossUp(df_list)
                    results_df['Symbol'] = i_stock_no
                    date_result = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]



                all_results = pd.concat([all_results, date_result], ignore_index=True)

        # rearrange the columns order
        cols = all_results.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        all_results = all_results[cols]
        all_results['Date'] = all_results['Date'].dt.strftime('%Y-%m-%d')


        js_results_str = all_results.to_json(orient='records')
        js_results = json.loads(js_results_str)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule_on_date(request, stock_no, rule_no, check_date):
    try:
        start_date = dt.datetime.strptime(check_date, "%Y%m%d") + dt.timedelta(-7)
        end_date = dt.datetime.strptime(check_date, "%Y%m%d") + dt.timedelta(+7)

        # Get the data from database
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$match": {"symbol":stock_no}},
            {"$match": {"k_data.Date" : { 
                        "$gt": start_date, 
                        "$lt": end_date
                    }}
            },
            {"$project":{ "k_data": {"$filter": {
                "input": '$k_data',
                "as": 'kdata',
                "cond": {"$and": [{"$gt": ['$$kdata.Date', start_date]},
                                {"$lt": ['$$kdata.Date', end_date]}
                        ]}}},
                "_id": 0
            }},
            {"$unwind": "$k_data"},
            {"$sort" : {  "k_data.Date" : 1  }  },
            {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
            {"$project": {"k_data": 1, "_id": 0}},
            ])

            # dataframe of a particular stock
        df = list(db_result)
        if df:
            df_list = pd.DataFrame(df[0]['k_data'])
            
            if rule_no == 0:
                # rule 0: sma cross-up strategy, SMA10 cross up SMA20
                results_df, b_flag = getSMACrossUp(df_list)
                results_df['Symbol'] = stock_no
                date_result = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]
            elif rule_no == 1:
                # rule 1: price cross-up sma strategy, Adj Close cross up SMA10
                results_df, b_flag = getPriceCrossUp(df_list)
                results_df['Symbol'] = stock_no
                date_result = results_df.loc[results_df['Date'] == dt.datetime.strptime(check_date, "%Y%m%d").strftime("%Y-%m-%d")]

        # rearrange the columns order
        cols = date_result.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        date_result = date_result[cols]
        if not date_result.empty:
            date_result['Date'] = date_result['Date'].dt.strftime('%Y-%m-%d')


        js_results_str = date_result.to_json(orient='records')
        js_results = json.loads(js_results_str)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET',])
def api_get_stock_score(request, stock_no, start_date, end_date):
    try:
        # Get the data from database
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$match": {"symbol":stock_no}},
            {"$match": {"k_data.Date" : { 
                        "$gt": dt.datetime.strptime(start_date, "%Y%m%d"), 
                        "$lt": dt.datetime.strptime(end_date, "%Y%m%d")
                    }}
            },
            {"$project":{ "k_data": {"$filter": {
                "input": '$k_data',
                "as": 'kdata',
                "cond": {"$and": [{"$gt": ['$$kdata.Date', dt.datetime.strptime(start_date, "%Y%m%d")]},
                                {"$lt": ['$$kdata.Date', dt.datetime.strptime(end_date, "%Y%m%d")]}
                        ]}}},
                "_id": 0
            }},
            {"$unwind": "$k_data"},
            {"$sort" : {  "k_data.Date" : 1  }  },
            {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
            {"$project": {"k_data": 1, "_id": 0}},
            ])

            # dataframe of a particular stock
        df = list(db_result)
        if df:
            df_list = pd.DataFrame(df[0]['k_data'])
            df_list['Symbol'] = stock_no
            df_list['Score'] = 0
            
            # rule 0: sma cross-up strategy, SMA10 cross up SMA20
            results_df, b_flag = getSMACrossUp(df_list)
            results_df['Score'] += 1
            df_list.update(results_df)
            
            # rule 1: price cross-up sma strategy, Adj Close cross up SMA10
            results_df, b_flag = getPriceCrossUp(df_list)
            results_df['Score'] += 1
            df_list.update(results_df)

        # rearrange the columns order
        cols = df_list.columns.tolist()
        cols = cols[-2:] + cols[:-2]
        df_list = df_list[cols]
        if not df_list.empty:
            df_list['Date'] = df_list['Date'].dt.strftime('%Y-%m-%d')


        js_results_str = df_list.to_json(orient='records')
        js_results = json.loads(js_results_str)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)

