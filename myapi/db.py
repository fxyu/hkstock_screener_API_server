from pymongo import MongoClient
from config import HOST
import datetime as dt

class DBClient:
    __host = HOST
    __db = None
    def __init__(self):
        DBClient.__db = MongoClient(DBClient.__host)

    @staticmethod
    def client():
        if DBClient.__db == None:
            DBClient.__db = MongoClient(DBClient.__host)
        return DBClient.__db


## Get all symbol
def db_get_data_by_symbol(stock_no,start_date,end_date,*args,**kwargs):
    '''
        db_get_all_symbol(stock_no,start_date,end_date) -> list

        keyword arguments
        stock_no        -- the symbol to search (e.g. 0001.HK)
        start_date      -- the starting date  (e.g. 20190215)
        end_date        -- the starting date  (e.g. 20190331)
    '''
    db = DBClient.client()
    col = db['hk-stock-db']['stock']

    db_result = col.aggregate([
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

    # TODO: handle np.nan problem
    db_result = list(db_result)
    if db_result:
        return db_result[0]['k_data']
    else:
        return None
    

def db_get_all_symbol():
    db = DBClient.client()
    col = db['hk-stock-db']['stock']

    db_result = col.aggregate([
            {"$group":{
                "_id": { "symbol" : "$symbol" },
                "symbol" : {"$first" : "$symbol" }
            }},
            {"$group": { "_id": "null",  "symbol": {  "$push": "$symbol"  }}},
            #{"$sort": {"symbol": 1}},
            {"$project":{"_id" : 0}},
        ])

    return list(db_result)


def db_get_triggered(symbol, start_date, end_date):
    db = DBClient.client()
    col = db['hk-stock-db']['rules_triggered']

    pipeline = []
    if symbol != None:
        pipeline.append({"$match": {"symbol": symbol}})

    pipeline.append({"$project": {"date": {"$filter": {
        "input": '$triggered',
        "as": 't',
        "cond": {"$and": [{"$gt": ['$$t.date', dt.datetime.strptime(start_date, "%Y%m%d")]},
                          {"$lt": ['$$t.date', dt.datetime.strptime(end_date, "%Y%m%d")]}
                          ]}}},
        "_id": 0,
        "symbol": 1
    }})
    pipeline.append({"$match": {'date.0': {"$exists": True}}})
    pipeline.append({"$unwind": "$date"})

    db_result = col.aggregate(pipeline)

    # import pdb; pdb.set_trace()
    return list(db_result)
