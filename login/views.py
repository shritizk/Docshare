from django.shortcuts import render, redirect



#dynmo db 
import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') #as we only have limited access to location , i made region static

#utils 
from .utils import table_checker

#hashing
import bcrypt



# task to be done in front end 
#create home.html  under home
#create sorry.html under Error
#complete signup.html

# task to be done in backend 
# input validation inside register_user function to be sure that we wont face exceptions in backend 
# create a login route : this route will send back a cookie ( jwt mostly ) used to verify user , also will store ip address with cookie inside a db 


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


# this is backend logic to register user 
def register_user(req):
    try : 
        #check for table / create table 
        res = table_checker('user')
        
        if(res == True):
            
            # get email , name and password of user to be updated inside the table 
            email = req.Post.get('email')
            name = req.Post.get('name')
            password = req.Post.get('password')
            
            
            # hash password to be stored 
            hashedPw = bcrypt.hashpw(password, bcrypt.gensalt())
            
            #store this inside dynamodb
            table = dynamodb.Table('user') # get access to table
            table_res = table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': hashedPw  
                    }
                )
                
            # redirect to login page
            return redirect('login')
                
                
    except ClientError as e  :
        # redirect to home sry page 
        print(e)
        return render(req, 'Error/sorry.html')
    
    except Exception as e:
        return redirect('signup')
        