from django.shortcuts import render , redirect
from django.contrib import messages
# hashing 
import jwt

#env 
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


#utils 
from  .utils import  s3_bucket

#dynmo db 
import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# front end 
def share_page(req):
    
    try :
        
        # jwt checker 
        session_token = req.COOKIES.get('session_token')
        if session_token:
            try:
                
                jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
                return render(req,'share_page.html')
            
            except jwt.ExpiredSignatureError:
                return redirect(req,'') 
            except jwt.InvalidTokenError:
                return redirect(req,'')  
                
    except Exception as e  :
        
        print(e)
        return render(req,'Error.html')  


    
    

#backend 

# search for user and return name of user based on search 
def search_user(req):
    
     # jwt checker 
        session_token = req.COOKIES.get('session_token')
        if session_token:
            try:
                
                decode =  jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
                
                user_email = req.POST.get('email')
              
                
                try : 
                    
                    # now search if user is authed 
                    table = dynamodb.Table('user')
                    
                    response = table.scan(
                        FilterExpression="email = :email",
                        ExpressionAttributeValues={":email": user_email})
                    
                 
                    
                    if response['Items']   : 
                        
                        # as we are expecting our user to share file to the 2nd user , lets first make cure this user have a bucket 
                        
                        # fetch jwt and decode to get user id 
                        # we have already done that while making user req user is authed 
                        
                        user_id = response['Items'][0].get('id')
                        
                        bucket_response = s3_bucket(decode.get('user_id')) # check or create bucket for sender 
                        
                        if  bucket_response == False : 
                            
                            messages.error(req, " con't perform this req right now , try again later  ")
                            
                            return render(req,'share_page.html')
                
                        return  redirect(req,f'{user_id}')
                        
                    else : 
                        
                        
                        messages.error(req, "email provided is wrong ")
                        return render(req,'share_page.html')
                    
                    
                except ClientError as e :
                    
                    print(e)
                    
                    return render(req,'Error.html')
                    
                
            
            except jwt.ExpiredSignatureError:
                return redirect(req,'') 
            except jwt.InvalidTokenError:
                return redirect(req,'')  
    
    
    
    
# send and store poge 
#def share_page(req):
    
    
    