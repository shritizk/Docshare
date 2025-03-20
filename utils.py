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
            
            
        
        
        