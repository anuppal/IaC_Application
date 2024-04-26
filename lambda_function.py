import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'Employee-Details'
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
        response = build_response(200)
    elif httpMethod == getMethod and path == employeePath:
        response = get_employee(event['queryStringParameters']['employeeID'])
    elif httpMethod == getMethod and path == employeesPath:
        response = get_employees()
    elif httpMethod == postMethod and path == employeePath:
        response = save_employee(json.loads(event['body']))
    elif httpMethod == patchMethod and path == employeePath:
        requestBody = json.loads(event['body'])
        response = modify_employee(requestBody['employeeID'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == employeePath:
        requestBody = json.loads(event['body'])
        response = delete_employee(requestBody['employeeID'])
    else:
        response = build_response(404, 'Not Found')
    return response


def get_employee(employeeID):
    try:
        response = table.get_item(
            Key={
                'employeeID': employeeID
            }
        )
        item = response.get('Item')
        if item:
            return build_response(200, item)
        else:
            return build_response(404, {"Message": f"Employee with ID {employeeID} not found"})
    except Exception as e:
        logger.exception('Custom handling for exceptions here: %s', str(e))
        return build_response(500, {"Message": "Internal Server Error"})


def get_employees():
    try:
        response = table.scan()
        items = response.get('Items', [])
        return build_response(200, {"employees": items})
    except Exception as e:
        logger.exception('Custom handling for exceptions here: %s', str(e))
        return build_response(500, {"Message": "Internal Server Error"})


def save_employee(requestBody):
    try:
        table.put_item(Item=requestBody)
        return build_response(200, {"Operation": "SAVE", "Message": "SUCCESS", "Item": requestBody})
    except Exception as e:
        logger.exception('Custom handling for exceptions here: %s', str(e))
        return build_response(500, {"Message": "Internal Server Error"})


def modify_employee(employeeID, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'employeeID': employeeID
            },
            UpdateExpression=f"set {updateKey} = :value",
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        return build_response(200, {"Operation": "UPDATE", "Message": "SUCCESS", "UpdatedAttributes": response})
    except Exception as e:
        logger.exception('Custom handling for exceptions here: %s', str(e))
        return build_response(500, {"Message": "Internal Server Error"})


def delete_employee(employeeID):
    try:
        response = table.delete_item(
            Key={
                'employeeID': employeeID
            },
            ReturnValues='ALL_OLD'
        )
        return build_response(200, {"Operation": "DELETE", "Message": "SUCCESS", "DeletedItem": response})
    except Exception as e:
        logger.exception('Custom handling for exceptions here: %s', str(e))
        return build_response(500, {"Message": "Internal Server Error"})


def build_response(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response
