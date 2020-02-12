from django.urls import path

from myapi.views import api_stock_data_all

app_name = 'stock_data'

urlpatterns = [

    # stock_no, start_date, end_date
    path('<str:stock_no>/<str:start_date>/<str:end_date>/', api_stock_data_all, name='stock_data_all')

]