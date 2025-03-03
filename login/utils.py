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
                    {"AttributeName": "email", "KeyType": "HASH"},
                    {"AttributeName": "id", "KeyType": "RANGE"}
                ],
                AttributeDefinitions=[
                    {"AttributeName": "email", "AttributeType": "S"},
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        table_created.wait_until_exists()
        return True

    except Exception as e:
        
        print(e)
        return False

