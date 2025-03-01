from django.urls import path
from . import views
urlpatterns = [
    path('register', views.register_user), # this is backend api call to user to be registered inside the db 
    path('signup',views.signup_page), # this will redirect to signup page 
    
]
