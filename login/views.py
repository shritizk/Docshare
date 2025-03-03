from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


# uuid 
import uuid 
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
# improve sorry to handle different type of error situation

# task to be done in backend 
# input validation inside register_user function to be sure that we wont face exceptions in backend 
# create a login route : this route will send back a cookie ( jwt mostly ) used to verify user , also will store ip address with cookie inside a db 
# on singup route do check if a user email already exist

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
        