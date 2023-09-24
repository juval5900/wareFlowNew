from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns=[
     path('adminindex/', views.adminindex, name='adminindex'),
     path('userspanel/', views.userspanel, name='userspanel'),
     path('add_user/', views.add_user, name='add_user'),
     path('get_user_details/<int:user_id>/', views.get_user_details, name='get_user_details'),
     path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
     path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),
     path('warehousepanel/', views.warehousepanel, name='warehousepanel'),
     path('add_warehouse/', views.add_warehouse, name='add_warehouse'),
           
    ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)