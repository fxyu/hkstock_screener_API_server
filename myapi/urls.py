from django.urls import path

from myapi.views import api_stock_data_all, api_get_all_symbol, api_check_rule_all, api_check_rule, api_check_rule_on_date_all, api_check_rule_on_date, api_get_stock_score

app_name = 'stock_data'

urlpatterns = [

    # stock_no, start_date, end_date
    # api/stock/<stock_no>/<start_date>/<end_date>/

    # currently, we have 2 rules for demo, 
    #   rule 0: sma10 cross-up sma20
    #   rule 1: adj close cross-up sma10
    
    # get data of <stock_no> from <start_date> to <end_date> from the database
    path('<str:stock_no>/<str:start_date>/<str:end_date>/', api_stock_data_all, name='stock_data_all'),

    # get all the stock symbols from the database
    path('symbol/', api_get_all_symbol, name='get_all_symbol'),

    # get stocks which fulfill rule <rule_no> within the date range <start_date> to <end_date>
    path('<str:start_date>/<str:end_date>/rule/<int:rule_no>/', api_check_rule_all, name='check_rule_all'),

    # get the date of fulfillment for <stock_no> fulfill rule <rule_no> during <start_date> to <end_date>
    path('<str:stock_no>/<str:start_date>/<str:end_date>/rule/<int:rule_no>/', api_check_rule, name='check_rule'),

    # get stocks which fulfill rule <rule_no> on a particular <check_date>
    path('<str:check_date>/rule/<int:rule_no>/on_date/', api_check_rule_on_date_all, name='check_rule_on_date_all'),

    # get whether <stock_no> fulfills rule <rule_no> on a particular <check_date>
    path('<str:stock_no>/<str:check_date>/rule/<int:rule_no>/on_date/', api_check_rule_on_date, name='check_rule_on_date'),

    # get scores of <stock_no> of each day from <start_date> to <end_date>
    # As currenlty we have 2 rules, max. score is 2.0, score ranges from 0.0 to 2.0
    path('<str:stock_no>/<str:start_date>/<str:end_date>/score/', api_get_stock_score, name='get_stock_score'),

]