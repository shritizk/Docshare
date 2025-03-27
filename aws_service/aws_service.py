import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def table_checker(Table_Name):
    try:
        table = dynamodb.Table(Table_Name)
        if table.table_status in ["ACTIVE", "UPDATING"]:
            return True     
        

    except ClientError as e:
        table_created = dynamodb.create_table(
            TableName=Table_Name, 
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}  # Use only 'id' as the primary key
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"}  # Define 'id' as a string type
            ],
            BillingMode="PAY_PER_REQUEST",
            )

        table_created.wait_until_exists()

        return True

    except Exception as e:
        
        print(e)
        return False


# s3 bucket creator 
def s3_bucket(bucket_name):
     
    try :
        
        s3_client = boto3.client('s3')
        
        s3_client.head_bucket(Bucket=bucket_name)
        
        return True
        
    except ClientError as e:
        
        try : 
            
            bucket_created = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}  
            )
            
            waiter = s3_client.get_waiter('bucket_exists')
            waiter.wait(Bucket=bucket_name)
            
            return True 
        
        except Exception as e:
            
            print(e)
            
            return False
            
            
def scan_dynmo(payload):
    
    try :
        
        if not payload: 
        
            return {"status": "payload_not_given"}
            
        else :    
            
            '''
            payload  = {
                search : user_id || email , 
                data : user_data
            }
            '''
            search = payload.get("search")
            data = payload.get("data")
            
            if search  == 'user_id':
                
                table = dynamodb.Table('user')
                
                response = table.scan(
                    FilterExpression="id = :id",
                    ExpressionAttributeValues={":id": data})
                
                if 'Items' not in response : 
                    
                    return {
                        "status" : False , 
                        "data" : {}
                    }
                
                else : 
                    
                    return {
                        "status" : True ,
                        "data" : response['Items'][0]
                    }
                
            elif search == 'email' : 
                
                table = dynamodb.Table('user')
                
                response = table.scan(
                    FilterExpression="email = :email",
                    ExpressionAttributeValues={":email": data})
                
                if 'Items' not in response : 
                    
                    return {
                        "status" : False , 
                        "data" : {}
                    }
                
                else : 
                    
                    return {
                        "status" : True ,
                        "data" : response
                    }
            
            else : 
                    
                return {
                        "status" : False , 
                        "response" : "Please provide a appropriate attribute to scan "
                    }
    except Exception as e : 
        
        print(e)
        
        return False
# send email

def sns_send_email(payload):
    
    try :
        
        if not payload: 
        
            return {"status": "payload_not_given"}
        
        ''' payload  = {
            arn , message , subject email
            
        }'''
        
        if not payload.get("arn") or not payload.get("email") or not payload.get("subject") or not payload.get("msg") :
            
            return {"status": "payload_not_given"}
        
        sns_client = boto3.client('sns', region_name="us-east-1")
        
        response = sns_client.publish(
                    TopicArn=payload.get("arn"),
                    Message=payload.get('msg'),
                    Subject=payload.get('subject'),
                    MessageAttributes={
                    'email': {
                'DataType': 'String',
                'StringValue': payload.get('email')}})
        
        return True 
        
    except Exception as e :
        
        print(e)
        
        return False

'''sns_client = boto3.client('sns', region_name="us-east-1")
                
                response = sns_client.publish(
                    TopicArn="arn:aws:sns:us-east-1:423091328531:EmailNotificationTopic",
                    Message="Your bio is just upgraded  !!",
                    Subject="Bio changed   ",
                    MessageAttributes={
                    'email': {
                'DataType': 'String',
                'StringValue': email }}) '''