from django.urls import path

from myapi.views import api_stock_data_all, api_get_all_symbol, api_check_rule_all, api_check_rule, api_check_rule_on_date_all, api_check_rule_on_date, api_get_stock_score

from myapi.views import api_check_multiple_rules

app_name = 'stock_data'

urlpatterns = [

    # stock_no, start_date, end_date
    # api/stock/<stock_no>/<start_date>/<end_date>/

    # currently, we have 8 rules for demo, 
    #   rule 0: sma10 cross-up sma20
    #   rule 1: sma10 cross-up sma50
    #   rule 2: Adj Close cross up SMA10
    #   rule 3: Adj Close cross up SMA20
    #   rule 4: Adj Close cross up SMA50
    #   rule 5: RSI14 cross-up 30
    #   rule 6: MACD cross-up strategy
    #   rule 7: Slow %K cross-up Slow %D strategy
    #   rule 8: price reach the BB Lowerband strategy
    ## the above are using cross-up/down strategies (spot out the trigger date)

    ## the below are simple comparing rules (*not only the trigger date)
    #   rule 9:     sma10 > sma20
    #   rule 10:    sma10 > sma50
    #   rule 11:    sma20 > sma50
    #   rule 12:    adj close > sma10
    #   rule 13:    adj close > sma20
    #   rule 14:    adj close > sma50
    #   rule 15:    adj close > sma100
    #   rule 16:    rsi < 80
    #   rule 17:    macd hist > 0   (i.e. macd line > signal line)
    #   rule 18:    slow %k > slow %d
    
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
    # As currenlty we have 18 rules, max. score is 18.0, score ranges from 0.0 to 18.0
    path('<str:stock_no>/<str:start_date>/<str:end_date>/score/', api_get_stock_score, name='get_stock_score'),

    # check multiple rules 
    # multiple rule no should be in the format of "1-2-3-4-6-8", i.e. checking rules 1,2,3,4,6,8
    path('check/<str:stock_no>/<str:start_date>/<str:end_date>/<str:rule_no>/', api_check_multiple_rules, name='check_multiple_rules'),

]