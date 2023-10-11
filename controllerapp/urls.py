from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns=[
    path('controllerindex/', views.controllerindex, name='controllerindex'),
    path('list_orders2/', views.list_orders2, name='list_orders2'),
    path('stock_list/', views.stock_list, name='stock_list'),
    path('update_stock/<int:stock_id>/', views.update_stock, name='update_stock'),
    path('get-stock-details/<int:stock_id>/', views.get_stock_details, name='get_stock_details'),
    path('get-stock-for-product/<int:product_id>/', views.get_stock_for_product, name='get_stock_for_product'),
    path('sales/', views.sales, name='sales'),
    path('add_sales/', views.add_sales, name='add_sales'),
    path("delete-multiple-sales/", views.delete_multiple_sales, name="delete_multiple_sales"),
    path('cancel_sale/<int:sale_id>/', views.cancel_sale, name='cancel_sale'),
    path('deliver_sale/<int:sale_id>/', views.deliver_sale, name='deliver_sale'),
    path('get-buying-price-for-stock/<int:stock_id>/', views.get_buying_price_for_stock, name='get_buying_price_for_stock'),
    path('controllercharts/', views.controllercharts, name='controllercharts'),
    path('get_profit_data/', views.get_profit_data, name='get_profit_data'),
    path('get_stock_and_sales_data/', views.get_stock_and_sales_data, name='get_stock_and_sales_data'),
    path('get_order_status_data/', views.get_order_status_data, name='get_order_status_data'),
    path('get_top_selling_products/', views.get_top_selling_products, name='get_top_selling_products'),
    path('get_sales_data/', views.get_sales_data, name='get_sales_data'),
    path('view_invoice/<int:sale_id>/', views.view_invoice, name='view_invoice'),
    
    ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)