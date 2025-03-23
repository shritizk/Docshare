from django.contrib import admin
from django.urls import path 

from . import views

urlpatterns = [
    
    # front end 
    path('',views.files_page),
    path('/remove',views.remove_file),
    
]
