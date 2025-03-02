import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def table_checker(Table_Name):
    try:
        table = dynamodb.Table(Table_Name)
        res = table.scan()
        items = res.get('Items', [])
        
        if items:
            return True
        else:
            dynamodb.create_table(
                TableName=Table_Name, 
                KeySchema=[
                    {"AttributeName": "email", "KeyType": "HASH"},
                    {"AttributeName": "id", "KeyType": "RANGE"}
                ],
                AttributeDefinitions=[
                    {"AttributeName": "email", "AttributeType": "S"},
                    {"AttributeName": "id", "AttributeType": "S"}
                ]
            )
            return True

    except ClientError as e:
        
        return False

    except Exception as e:
        
        print(e)
        return False

