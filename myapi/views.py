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
import pdb

from .operator import *

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
        db_result = db_get_all_symbol()
        sorted_list = get_symbol_list_arr(db_result)
        js_results = get_check_rule_results_all(
                        sorted_list, 
                        rule_no, 
                        start_date, 
                        end_date, 
                        0, 
                        False)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule(request, stock_no, rule_no, start_date, end_date):
    try:
        # Check <rule_no> of <stock_no> from <start_date> to <end_date>
        js_results = get_check_rule_results(stock_no, rule_no, start_date, end_date, 0, False)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule_on_date_all(request, rule_no, check_date):
    try:
        start_date, end_date = get_start_end_dates(check_date)
        # Get the symbol list from database
        db_result = db_get_all_symbol()
        js_results = get_check_rule_results_all(get_symbol_list_arr(db_result), rule_no, start_date, end_date, check_date, True)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_rule_on_date(request, stock_no, rule_no, check_date):
    try:
        start_date, end_date = get_start_end_dates(check_date)
        # Check <rule_no> of <stock_no> on <check_date>
        js_results = get_check_rule_results(stock_no, rule_no, start_date, end_date, check_date, True)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_get_stock_score(request, stock_no, start_date, end_date):
    try:
        # Get scores of <stock_no> from <start_date> to <end_date>
        js_results = get_stock_score(stock_no, start_date, end_date)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET',])
def api_check_multiple_rules(request, stock_no, start_date, end_date, rule_no):
    try:
        # check whether <stock_no> fulfill multiple rules <rule_no> from <start_date> to <end_date>
        arr_rule_no = rule_no.split('-')
        js_results = check_multiple_rules(stock_no, start_date, end_date, arr_rule_no)

        if request.method == "GET":
            return Response(js_results)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        return Response(status=status.HTTP_404_NOT_FOUND)

