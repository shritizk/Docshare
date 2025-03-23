
from django.contrib import admin
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('login.urls')), # this path contain all the signup and login urls  
    path('dashboard',include('dashboard.urls')), # dashboard app urls file
    path('share/',include('share.urls')),
    path('files',include('files.urls')),

]
