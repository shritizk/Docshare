from django.urls import path
from .views import signup_page ,  register_user , home_page
urlpatterns = [
    
    path('',home_page),# this will render home page
    path('signup',signup_page), # this will redirect to signup page 
    path('login',signup_page),
    
    #backend routes
    path('register/', register_user), # this is backend api call to user to be registered inside the db 
    
]
