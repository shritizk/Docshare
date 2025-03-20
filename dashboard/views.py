from django.shortcuts import render
from django.shortcuts import render, redirect


# imports 
import json
import jwt
import os

#keys
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

#front end 

# main dashboard html
def dashboard_page(req):
    
   # get cookies
   
   session_token = req.COOKIES.get('session_token')
   try:

      if session_token:
            
         decode = jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
               
         if decode :
                  
            content = {
                     'id': decode.get('user_id'),
                     'email': decode.get('email'),
                     'name': decode.get('name'),
                     'bio': decode.get('bio', ''),
                  }
                  
            return render(req, 'dashboard/dashboard.html' , content)
                  
                  
   except Exception as e   :
      
      print(e)
      
      return render(req,'dashboard/Error.html')
      
      
      
   
# backend 