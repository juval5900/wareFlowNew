from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns=[
    path('qualityindex/', views.qualityindex, name='qualityindex'),
    path('quality_profile/', views.quality_profile, name='quality_profile'),
    path('order_list/', views.order_list, name='order_list'),
    path('get_inspection_data/', views.get_inspection_data, name='get_inspection_data'),
    path('save_inspection/<int:order_id>/', views.save_inspection, name='save_inspection'),
    path('inspection_list/', views.inspection_list, name='inspection_list'),
    path('print_inspection_report/<int:order_id>/', views.print_inspection_report, name='print_inspection_report'),
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)