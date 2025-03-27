from django.shortcuts import render , redirect 
from django.contrib import messages
from django.http import FileResponse , HttpResponse

import tempfile

# jwt 
import jwt 

# utils 
from aws_service.aws_service import *

#env 
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# boto
import boto3
from botocore.exceptions import ClientError


def files_page(req):
    
    try :
        
        session_token = req.COOKIES.get('session_token')
        
        if session_token : 
            
            try : 
                
                session_token = jwt.decode(session_token,SECRET_KEY, algorithms=['HS256'])
                
                # create content 
                
                user_id = session_token.get('user_id')
                
                # check or create s3 bucket for this user
                
                user_bucket = s3_bucket(user_id)
                
                if user_bucket == False : 
                    
                    messages.error(req, " can not load file page write now , try again later !! ")
                    return redirect('/')
                
                # now use user_id to get s3 data 
                
                s3_client = boto3.client('s3',region_name='us-east-1')
                
                obj_list = s3_client.list_objects_v2(Bucket=user_id) 
                
                file_name = [obj["Key"] for obj in obj_list.get("Contents", [])]
                
                if file_name == [] : 
                    
                    content = []
                    
                    return render(req, 'files.html', content ) 
                    
                
                received_files = []
                
                user_files = []
                
                file_keys = []
                
                for i in file_name : 
                    
                    if len(i.split('+'))  >= 4 : 
                        
                        url = s3_client.generate_presigned_url('get_object',
                        Params={'Bucket': user_id, 'Key': i},
                        ExpiresIn=3600)
                        
                        received_files.append( {'name': i.split('+')[-1], 'url': url ,  'file_key' : i})
                        
                    if  len(i.split('+')) == 3 :
                        
                        url = s3_client.generate_presigned_url('get_object',
                        Params={'Bucket': user_id, 'Key': i},
                        ExpiresIn=3600)
                        
                        user_files.append( {'name': i.split('+')[-1], 'url': url , 'file_key' : i })
                        
                     
                        
                content = {
                    'received_files' :  received_files , 
                    'user_file' : user_files 
                }
                
                # format 
                ''' 
                {
        'received_files': received_files,
        'user_files': user_files,
    }
                
                '''
                
                return render(req, 'files.html', content )        
                
                
            except jwt.ExpiredSignatureError:
            
                return redirect(req,'/') 
    
            except jwt.InvalidTokenError:
    
                return redirect(req,'/')         
    
    
        return render(req, 'files.html')
    
    except Exception as e:
        
        print(e)
        
        return redirect('/') 
        


def remove_file(req ):
    
    # this function is to remove files from s3 bucket of that user 
    
    try :
        
        session_token = req.COOKIES.get('session_token')
        
        if session_token : 
            
            try : 
                
                session_token = jwt.decode(session_token,SECRET_KEY, algorithms=['HS256'])
                
                user_id = session_token.get('user_id')
                
                s3_client = boto3.client('s3', region_name='us-east-1')
                
                # get file name 
                
                file_key = req.POST.get("file_key")
                
                if file_key == None : 
                    
                    messages.error(req, " can not load file page write now , try again later !! ")
                    return redirect('/')
                
                try :     
                        
                    s3_client.delete_object(Bucket=user_id, Key=file_key)
                    
                    
                    return redirect('/files')
                    
                except Exception as e:
                    
                    print(e)
                    return redirect('/files')
                    
            except Exception as e:
                
                print(e)
                
                messages.error(req, " can not load file page write now , try again later !! ")
                return redirect('/')
                
            
    except jwt.ExpiredSignatureError:
            
        return redirect(req,'/') 
    
    except jwt.InvalidTokenError:
    
        return redirect(req,'/')        
    
    except Exception as e:
        
        print(e)
        
        return redirect(req,'/')
        