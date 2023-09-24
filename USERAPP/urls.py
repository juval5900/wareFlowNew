from django.urls import path
from USERAPP import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from .views import ExportPDF
from .views import ExportSupplierPDF,ExportOrdersPDF

urlpatterns = [
    path('index/',views.index, name='index'),
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('loggout',views.loggout,name='loggout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('check_email/', views.check_email, name='check_email'),
    path('check_username/', views.check_username, name='check_username'),
    path('notifications',views.notifications,name='notifications'),
    path('error',views.error,name='error'),
    path('account',views.account,name='account'),
    path('charts',views.charts,name='charts'),
    path('docs',views.docs,name='docs'),
    path('help',views.help,name='help'),
    path('inventory',views.inventory,name='inventory'),
    path('settingshtml',views.settingshtml,name='settingshtml'),
    
    path('add_product/', views.add_product, name='add_product'),
    path('list_products/', views.list_products, name='list_products'),
    path('accounts/', include('allauth.urls')),
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update-product/<int:product_id>/', views.update_product, name='update-product'),
    path('get-product-details/<int:product_id>/', views.get_product_details, name='get-product-details'),
    path('delete-multiple-products/', views.delete_multiple_products, name='delete_multiple_products'),
    
    path('add_suppliers/', views.add_suppliers, name='add_suppliers'),
    path('list_suppliers/', views.list_suppliers, name='list_suppliers'),
    path('delete-suppliers/<int:supplier_id>/', views.delete_suppliers, name='delete_suppliers'),
    path('update-supplier/<int:supplier_id>/', views.update_supplier, name='update-supplier'),
    path('get-supplier-details/<int:supplier_id>/', views.get_supplier_details, name='get-supplier-details'),
    path('delete-multiple-suppliers/', views.delete_multiple_suppliers, name='delete_multiple_suppliers'),
    path('check_suppliercontact/', views.check_suppliercontact, name='check_suppliercontact'),
    path('check_supplieremail/', views.check_supplieremail, name='check_supplieremail'),
    
    
    path('add_orders/', views.add_orders, name='add_orders'),
    path('list_orders/', views.list_orders, name='list_orders'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('deliver_order/<int:order_id>/', views.deliver_order, name='deliver_order'),
    path('update_order/<int:order_id>/', views.update_order, name='update_order'),
    path('get-order-details/<int:order_id>/', views.get_order_details, name='get-order-details'),
    path('cancel-multiple-orders/', views.cancel_multiple_orders, name='cancel_multiple_orders'),
    path('return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('returned_order/<int:order_id>/', views.returned_order, name='returned_order'),
    path('profile_view', views.profile_view, name='profile_view'),
    
    path('allocate_storages/<int:order_id>/', views.allocate_storages, name='allocate_storages'),
    path('add_storage', views.add_storage, name='add_storage'),
    path('list_storage', views.list_storage, name='list_storage'),
    path('export_pdf/', ExportPDF.as_view(), name='export_pdf'),
    path('export_supplier_pdf/', ExportSupplierPDF.as_view(), name='export_supplier_pdf'),
    path('export_orders_pdf/', ExportOrdersPDF.as_view(), name='export_orders_pdf'),
    path('generate_otp', views.generate_otp, name='generate_otp'),
    path('forgot', views.forgot, name='forgot'),
    path('reset_password/', views.reset_password, name='reset_password'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)