from django.urls import path
from . import views
urlpatterns = [
    
    path('',views.home_page),# this will render home page
    path('signup',views.signup_page), # this will redirect to signup page 
    path('login',views.login_page),
    
    #backend routes
    path('register', views.register_user), # this is backend api call to user to be registered inside the db 
    path('signin',views.login_user),
    path('logout',views.logout_user),
    
    # edit user Data 
    path('newbio',views.new_bio)
    
]
