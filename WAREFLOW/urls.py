# project/urls.py
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('', include('USERAPP.urls')),  # Replace 'your_app' with your app's name
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('ADMINAPP.urls')),
    path('', include('controllerapp.urls')),
]
