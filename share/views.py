from django.shortcuts import render , redirect
from django.contrib import messages

# import 
import datetime

# hashing 
import jwt
import json

#env 
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
QueueUrl = os.getenv("q_url")

#utils 
from  .utils import  s3_bucket , table_checker

#dynmo db 
import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# front end 


            
def share_page(req):
    
    session_token = req.COOKIES.get('session_token')
    if session_token :
        try:
            
            # get user data 
            decode = jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
    
            user_id = decode.get('user_id')
            
            bucket_check = s3_bucket(user_id)
            
            if bucket_check == False : 
                
                return redirect('/')
            
            # get user objs from bucket 
            s3_client = boto3.client('s3',region_name='us-east-1')
                    
            obj_list = s3_client.list_objects_v2(Bucket=user_id) 
                        
            file_keys = [obj["Key"] for obj in obj_list.get("Contents", [])]
            
            
            if  not file_keys: 
                
                # send empty 
                return render(req,'share_page.html' )
            
            file_list = []
            
            for i in file_keys:
                
                if len(i.split('+')) == 3:
                    
                    file_list.append(i.split('+')[-1])
                
                # send this as to render page without msg 
            return render(req,'share_page.html', { "file_names": file_list })
            
            
        except jwt.ExpiredSignatureError:
            return redirect(req,'/') 
        except jwt.InvalidTokenError:
            return redirect(req,'/')  
    

    

def store_files(req):
    
    # verify jwt from user 
 
          
        session_token = req.COOKIES.get('session_token')
        if session_token : 
        
            try:
            
                decode = jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
                user_id = decode.get('user_id')
                
                
                if 'file' not in req.FILES or req.FILES['file'] is None:
                    
                    messages.error(req, " no file provided ")
                    
                    return redirect('/share/') 
                
                else :
                    
                    #get file from front end 
                    uploaded_file = req.FILES['file']
                    
                    # client 
                    s3_client = boto3.client('s3',region_name='us-east-1')
                    
                    obj_list = s3_client.list_objects_v2(Bucket=user_id) 
                        
                    file_keys = [obj["Key"] for obj in obj_list.get("Contents", [])]
                    
                    if len(file_keys) >= 3 :
                        
                        messages.error(req, " You can not upload more then 3 files at a time , please go to managment clear data !! ")
                        
                        return redirect('/share/') 
                
                    else :
                        
                        # set upload name , prefix with user_id and date , split with " +  ""
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                        upload_name = f"{user_id}+{current_date}+{uploaded_file.name}"
                        
                        try : 
                            
                            s3_client.upload_fileobj(uploaded_file, user_id, upload_name)
                            
                            messages.error(req, " file added !! ")
                            
                            return redirect('/share/') 
                            
                        except Exception as e :
                            
                            print(e)

                            messages.error(req, " file can not be added  !! ")
                            
                            return redirect('/share/')                    
            
            except jwt.ExpiredSignatureError:
            
                return redirect(req,'/') 
    
            except jwt.InvalidTokenError:
    
                return redirect(req,'/')  
                        
   
        # also i want to add this : if user already have 3 files stored in s3 , dont let it add file to bucket ` -done 
    
    


def send_file(req):
    session_token = req.COOKIES.get('session_token')
    if session_token:
        try:
            decode = jwt.decode(session_token, SECRET_KEY, algorithms=["HS256"])
            user_id = decode.get('user_id')
            receiver_email = req.POST.get('receiver_email')

            if not receiver_email:
                return redirect('/share/')

            # Check if user exists
            table_checker('user')
            table = dynamodb.Table('user')
            response = table.scan(
                FilterExpression="email = :email",
                ExpressionAttributeValues={":email": receiver_email}
            )

            if 'Items' not in response:
                return redirect('/share/')
            
            destination_bucket = response['Items'][0].get('id')

            # Get file name to send
            file_to_send = req.POST['file_to_send']
            if not file_to_send:
                messages.error(req, "No file selected to send!")
                return redirect('/share/')
            
            # Check sender's bucket
            sender_check = s3_bucket(user_id)
            if sender_check == False:
                messages.error(req, "Cannot perform this action right now!")
                return redirect('/share/')

            # Get sender's file names from S3
            s3_client = boto3.client('s3', region_name='us-east-1')  # Ensure region_name is specified
            sender_data = s3_client.list_objects_v2(Bucket=user_id)
            file_names = [obj["Key"] for obj in sender_data.get("Contents", [])]

            if not file_names:
                messages.error(req, "No files available in your bucket!")
                return redirect('/share/')

            file_status = None
            for i in file_names:
                if len(i.split('+')) == 3:
                    if i.split('+')[-1] == file_to_send:
                        file_status = i
                        break

            if not file_status:
                messages.error(req, "File not found in your bucket!")
                return redirect('/share/')

            # Create copy source
            copy_source = {'Bucket': user_id, 'Key': file_status}

            # Sending logic
            try:
                destination_check = s3_bucket(destination_bucket)
                if destination_check:
                    reciver_key = f"{destination_bucket}+recived_from=+{copy_source.get('Bucket')}+{file_status}"
                    s3_client.copy_object(
                        Bucket=destination_bucket,
                        CopySource=copy_source,
                        Key=reciver_key
                    )

                    # Send message to SQS
                    sqs_client = boto3.client('sqs', region_name='us-east-1')  # Ensure region_name is specified
                    sqs_client.send_message(
                        QueueUrl=QueueUrl,
                        MessageBody=json.dumps({
                            'file_name': reciver_key,
                            'bucket': destination_bucket,
                            'destination_email': receiver_email
                        }),
                        DelaySeconds=900
                    )

                    messages.error(req, "File sent successfully!")
                    return redirect('/share/')
                else:
                    messages.error(req, "Can't reach this user at this time!")
                    return redirect('/share/')
            except Exception as e:
                logger.error(f"Error during file sending: {str(e)}")
                messages.error(req, "Something went wrong, can't send file right now. Try again later.")
                return redirect('/share/')
        except jwt.ExpiredSignatureError:
            return redirect('/')
        except jwt.InvalidTokenError:
            return redirect('/')