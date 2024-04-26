import json
import boto3
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName='Employee-Details'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
employeePath = '/employee'
employeesPath = '/employees'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
        
    elif httpMethod == getMethod and path == employeePath:
        response = getEmployee(event['queryStringParameters']['employeeID'])
    elif httpMethod == getMethod and path == employeesPath:
        response = getEmployees(event['queryStringParameters']['employeeID'])  
    elif httpMethod == postMethod and path == employeePath:
        response = saveEmployee(json.loads(event['body']))       
    elif httpMethod == patchMethod and path == employeePath:
        requestBody = json.loads(event['body'])
        response = modifyEmployee(requestBody['employeeID'],requestBody['updateKey'],requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == employeePath:
        requestBody = json.loads(event['body'])
        response = deleteMethods(requestBody['employeeID'])
    else:
        response = buildResponse(404,'Not Found')
    return response


def getEmployee(employeeID):
    try:
        response = table.get_item(
            key={
                'employeeID': employeeID
            }
        )
        if item in response:
            return buildResponse(200, response('Item'))
        else:
            return buildResponse(404, f'{{"Message {employeeID} Not found"}}')
    except:
        logger.exception{'Do your custom handling here. I am just gona log it out here '}


def getEmployees():
    try:
        response = table.scan()
        result = response['Item']

        while 'LastEvalauatedkey' in response:
            respnose = table.scan(ExclusiveStartKey=respnose['LastEvalauatedkey'])
            result.extend(respnose['Item'])
        
        body={
            'employees': result
        }
        return buildResponse(200, body)
    except Exception as e:
        # Exception handling
        logger.exception("An error occurred: %s", str(e))
        # Additional custom handling can be done here

def saveEmployee(requestBody):
    try:
        table.put_item(item=requestBody)
        body={
            'Operation':'SAVE',
            'Message':'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except Exception as e:
        # Exception handling
        logger.exception("An error occurred: %s", str(e))
        # Additional custom handling can be done here

def modifyEmployee(employeeID,updateKey,updateValue):
    try:
        response = table_update_item(
            Key={
                'employeeID': employeeID
            },
            UpdateExpression = f'set {updateKey} = :value',
            ExpressionAttributeValues={
                ':value':updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body={
            'Operation':'SAVE',
            'Message':'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except Exception as e:
        # Exception handling
        logger.exception("An error occurred: %s", str(e))
        # Additional custom handling can be done here

def deleteMethods(employeeID):
    try:
        response = table.delete_item(
            Key={
                'employeeID': employeeID
            },
            ReturnValues='ALL_OLD'  # Corrected parameter name
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deleteItem': response
        }
        return buildResponse(200, body)
    except Exception as e:
        logger.exception("An error occurred: %s", str(e))



def buildResponse(statusCode,body=None):
    response = {
        'statusCode':statusCode,
        'headers':{
            'content-type':'application/json',
            'Access-Control-Allow-Origin':'*'
        }
    }
    if body is not None:
        response['body']= json.dumps(body)
        return response