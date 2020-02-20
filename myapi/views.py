from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from pymongo import MongoClient
from .db import DBClient as db
import pandas as pd
import datetime as dt
from pprint import pprint

import pickle
import base64
import sys
import json

from .rules import getSMACrossUp

# Create your views here.
@api_view(['GET',])
def api_stock_data_all(request, stock_no, start_date, end_date):
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
            {"$sort" : {  "k_data.date" : 1  }  },
            {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
            {"$project": {"k_data": 1, "_id": 0}},
            ])
            
        df_list = list(db_result)
        # TODO: handle np.nan problem
        # pprint(df_list)
        # df = pd.DataFrame(list(db_result)[0]['k_data']) 
        if request.method == "GET":
            # pickled = pickle.dumps(df)
            # pickled_b64 = base64.b64encode(pickled)
            return Response(df_list)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET',])
def api_get_all_symbol(request):
    try:
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$group":{
                "_id": { "symbol" : "$symbol" },
                "symbol" : {"$first" : "$symbol" }
            }},
            {"$group": { "_id": "null",  "symbol": {  "$push": "$symbol"  }}},
            #{"$sort": {"symbol": 1}},
            {"$project":{"_id" : 0}},
        ])

        df_list = list(db_result)

        if request.method == "GET":
            return Response(df_list)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule_all(request, start_date, end_date):
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
        # just test the first 10 stocks
        # ------------------------------------
        for i_stock_no in arr_stock_list[:10]:
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
                {"$sort" : {  "k_data.date" : 1  }  },
                {"$group": {  "_id": "null",  "k_data": {  "$push": "$k_data"  }   }},
                {"$project": {"k_data": 1, "_id": 0}},
                ])

            # dataframe of a particular stock
            df_list = pd.DataFrame(list(db_result)[0]['k_data'])
            if bFirstStock == True:
                all_results = df_list.copy()
                all_results.drop(all_results.index, inplace=True)
                all_results['Symbol'] = []
                bFirstStock = False

            #if rule_no == 0:
                # rule 0: sma cross-up strategy, SMA10 cross up SMA20
            results_df, b_flag = getSMACrossUp(df_list)
            results_df['Symbol'] = i_stock_no
            

            all_results = pd.concat([all_results, results_df], ignore_index=True)

        # rearrange the columns order
        cols = all_results.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        all_results = all_results[cols]
        all_results['Date'] = all_results['Date'].dt.strftime('%Y-%m-%d')


        js_results = all_results.to_json(orient='records')

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)
