from django.urls import path , include
from . import views



urlpatterns = [
    
    
    # front end 
    path('',views.share_page),
    
    # backend 
    path('search',views.search_user),
    #path('<int:user_id>/',views.search_page)
       
]