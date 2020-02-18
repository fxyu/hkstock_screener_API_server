from django.urls import path

from myapi.views import api_stock_data_all, api_get_all_symbol

app_name = 'stock_data'

urlpatterns = [

    # stock_no, start_date, end_date
    # api/stock/<stock_no>/<start_date>/<end_date>/
    path('<str:stock_no>/<str:start_date>/<str:end_date>/', api_stock_data_all, name='stock_data_all')
    path('symbol/', api_get_all_symbol, name='get_all_symbol')

]