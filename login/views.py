from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

# async 
import asyncio

# uuid 
import uuid 

#token
import jwt
import json

# env 
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
arn = os.getenv("arn")

#dynmo db 
import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 

#utils 
from .utils import *

#hashing
import bcrypt

# clients 
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('user')
sns_client = boto3.client('sns', region_name="us-east-1")


# task to be done in front end 
#create home.html  under home - done
#create sorry.html under Error - done 
#complete signup.html -done 
# create login.html under user -done
# create route to render to user - done
# improve sorry to handle different type of error situation -done
# created a user already exist html file ass well and also done with logic part  - done
# if user is loged in edit home to new template -done
# if user enter wrong password change it - done 

# task to be done in backend 
# input validation inside register_user and login_user function to be sure that we wont face exceptions in backend 
# create a login route : this route will send back a cookie ( jwt mostly ) used to verify user - done
# on singup route do check if a user email already exist -done

# Create your views here.


#this one will redirect to home page 



def home_page(req):
    try:
        session_token = req.COOKIES.get('session_token')

        if session_token:
            try:
                jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
                logged_in = True  
            except jwt.ExpiredSignatureError:
                logged_in = False 
            except jwt.InvalidTokenError:
                logged_in = False  
        else:
            logged_in = False  

        return render(req, 'home/home.html', {'logged_in': logged_in })

    except Exception as e:
        print(e)
        return render(req, 'Error/sorry.html')

# this will redirect to signup form 
def signup_page(req):
    try : 
       return render(req, 'user/signup.html')
    except : 
        return render(req, 'Error/sorry.html')

# this will render login page
def login_page(req):
    try : 
        return render(req , 'user/login.html')
    except : 
        return render(req, 'Error/sorry.html')


# this is backend logic to register user 
@csrf_exempt
def register_user(req):
    try : 
            
        # get email , name and password of user to be updated inside the table 
        email = req.POST.get('email')
        name = req.POST.get('name')
        password = req.POST.get('password')
            
            
        # hash password to be stored 
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
        #check for table / create table 
        res = table_checker('user')
        
        #add to table 
        table = dynamodb.Table('user')
        
        # checking if email already exist 
        
        response = table.scan(
            FilterExpression="email = :email",
            ExpressionAttributeValues={":email": email})
        
        
    
        if response['Items']: 
            return render(req, 'Error/userAlreadyExist.html')
            #uuid 
        unique_id = str(uuid.uuid4())
        
        added_to_table = table.put_item(
        Item={
                'id' : unique_id, 
                'email': email,
                'name': name,
                'password': hashed_pw
        })

       
        # Subscribe user to SNS for email verification
        sns = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )
        
        
                
        # redirect to login page
        return redirect('/login')      
        
      
      
                
                
    except ClientError as e  :
        # redirect to home sry page 
        print(e)
        return render(req, 'Error/sorry.html')
    
    except Exception as e:
        
        print()
        return redirect('/signup')
        
        
        
@csrf_exempt
def login_user(req):
    # this route will take email and password check them and send cookie in return 
    # also will store that cookie , ip and user email inside a table in db to keep a track
    
    try :
        
        #take data from req body
        user_email = req.POST.get('email')
        password = req.POST.get('password')
        # input validation function to be called 
        
        
        table = dynamodb.Table('user')
        
        # response = table.scan(
        #     FilterExpression="email = :email",
        #     ExpressionAttributeValues={":email": user_email})
        response = table.query(
                IndexName="EmailIndex",
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email":user_email})
        
        print('response',response)
        if response['Items']:
            user_password = response['Items'][0].get('password')
            password_result = bcrypt.checkpw(password.encode('utf-8'), user_password.encode('utf-8'))
            
            user_id = response['Items'][0].get('id')
            user_name = response['Items'][0].get('name')
            user_bio = response['Items'][0].get('name') or ""            
            print('pass result',password_result)
            if(password_result ==True):
                session_token = jwt.encode({
                    'user_id' : user_id,
                    'email' : user_email ,
                    'name' : user_name ,
                    'bio' : user_bio
                },
                SECRET_KEY )
                print(session_token)
                user_email = response['Items'][0].get('email')
                user_name = response['Items'][0].get('name')
                user_id = response['Items'][0].get('id')
                user_bio = response['Items'][0].get('bio') or  ""
                
                user_data =  {
                    'id' : user_id ,
                    'email' :user_email,
                    'username' : user_name,
                    'bio' : user_bio
                }
                
                # send email
                
                sns_client = boto3.client('sns', region_name="us-east-1")
                
                response = sns_client.publish(
                    TopicArn="arn:aws:sns:us-east-1:423091328531:EmailNotificationTopic",
                    Message="You have just loged in at doc ",
                    Subject="Loged in at doc share ",
                    MessageAttributes={
                    'email': {
                'DataType': 'String',
                'StringValue': user_email  }})
                
                response = redirect('/dashboard/profile')
                response.set_cookie('session_token', session_token)
                

                return response
            else : 
                return render(req,'Error/wrongPass.html')
       
        else : 
            print('sorry')
            return render(req, 'Error/sorry.html')
            
        
    except ClientError as e  :
        # redirect to home sry page 
        print(e)
        return render(req, 'Error/sorry.html')
    
    except Exception as e:
        
        print(e)
        return render(req, 'Error/sorry.html')
        
def logout_user(request):
    response = HttpResponseRedirect('/')  
    response.delete_cookie('session_token')
    response.delete_cookie('content')
    return response
    
    

# edit bio            
def new_bio(req) : 
    
    session_token = req.COOKIES.get('session_token')
    try:

      if session_token:
            
        decode = jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
               
        if decode:
                  
            user_id = decode.get('user_id')
            
            new_bio = req.POST.get('bio')
            
            table = dynamodb.Table('user')
            
            email =  decode.get('email')
            
            response = table.update_item(
            Key={'id': user_id  },
            UpdateExpression="SET bio = :bio",
            ExpressionAttributeValues={
                ':bio': new_bio
            },
            ReturnValues="UPDATED_NEW"
            )
            
            if 'Attributes' in response:
                
                
                sns_res = sns_send_email({
                    "arn" : arn , 
                    "msg" : "Your bio is just upgraded  !!" , 
                    "subject" : "Bio changed !!" , 
                    "email" : email
                })
                
                response =  scan_dynmo({
                    "search" : 'user_id' , 
                    "data" : user_id
                })
                
                if response.get("status") == False : 
                    
                    return render(req, 'Error/sorry.html')
                
                user_email = response['Items'][0].get('email')
                user_name = response['Items'][0].get('name')
                user_id = response['Items'][0].get('id')
                user_bio = response['Items'][0].get('bio') or  ""
                
                session_token = jwt.encode({
                    'user_id' : user_id,
                    'email' : user_email ,
                    'name' : user_name ,
                    'bio' : user_bio
                },
                SECRET_KEY  )
                
                user_data =  {
                    'id' : user_id ,
                    'email' :user_email,
                    'username' : user_name,
                    'bio' : user_bio
                }
                
                response = redirect('/dashboard/profile')
                response.set_cookie('session_token', session_token)   
                return response
                
            else:
                
                return render(req, 'Error/sorry.html')
                  
    except Exception as e   :
      
        print(e)
        return render(req, 'Error/sorry.html')
        
    