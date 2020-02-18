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
def api_get_all_symbol(request)
    try:
        stock_collection = db.client()['hk-stock-db']['stock']

        db_result = stock_collection.aggregate([
            {"$group":{
                "_id": { "symbol" : "$symbol" },
                "symbol" : {"$first" : "$symbol" }
            }},
            {"$group": {  "_id": "null",  "symbol": {  "$push": "$symbol"  }   }},
            {"$project":{"_id" : 0}},
        ])

        df_list = list(db_result)

        if request.method == "GET":
            return Response(df_list)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)

    