from django.urls import path , include

from . import views



urlpatterns = [
    
    
    # front end 
    path('',views.share_page), # front end to search user 
    path('store',views.store_files) ,
    path('send',views.send_file)
   
]