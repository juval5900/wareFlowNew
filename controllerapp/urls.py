from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns=[
    path('controllerindex/', views.controllerindex, name='controllerindex'),
    path('list_orders2/', views.list_orders2, name='list_orders2'),
    ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)