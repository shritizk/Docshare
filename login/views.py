from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

# async 
import asyncio

# uuid 
import uuid 

#token
import jwt
from datetime import datetime


#dynmo db 
import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') #as we only have limited access to location , i made region static

#utils 
from .utils import table_checker

#hashing
import bcrypt



# task to be done in front end 
#create home.html  under home - done
#create sorry.html under Error - done 
#complete signup.html -done 
# create login.html under user -done
# create route to render to user - done
# improve sorry to handle different type of error situation -done
# created a user already exist html file ass well and also done with logic part  - done

# task to be done in backend 
# input validation inside register_user and login_user function to be sure that we wont face exceptions in backend 
# create a login route : this route will send back a cookie ( jwt mostly ) used to verify user - done
# on singup route do check if a user email already exist -done

# Create your views here.


#this one will redirect to home page 
def home_page(req):
    try : 
        return render(req, 'home/home.html')
    except : 
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
        
        
    
        if response['Items']:  # If the user exists, show error
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

                
        # redirect to login page
        return HttpResponseRedirect('/login')    
        
      
      
                
                
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
        
        response = table.scan(
            FilterExpression="email = :email",
            ExpressionAttributeValues={":email": user_email})
        
        
    
        if response != [] :
            user_password = response['Items'][0].get('password')
            password_result = bcrypt.checkpw(password.encode('utf-8'), user_password.encode('utf-8'))
            
            if(password_result ==True):
                now = datetime.now()
                session_token = jwt.encode({
                    'date' : now , 
                    'email' : user_email ,
                    'password' : password
                },
                "dsjnskg"  , 
                algorithms=["HS256"])
                
                return response.set_cookie('session_token', session_token )
        else : 
            
            return render(req, 'Error/sorry.html')
            
        
    except ClientError as e  :
        # redirect to home sry page 
        print(e)
        return render(req, 'Error/sorry.html')
    
    except Exception as e:
        
        print(e)
        return render(req, 'Error/sorry.html')