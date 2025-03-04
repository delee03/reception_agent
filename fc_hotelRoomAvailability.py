import json
import boto3

client_dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
#Store the user input - date to check room availability
    # print(f"The user input {event['checkInDate']}")
    # user_input_date = event['checkInDate']
    user_input_date = event['parameters'][0]['value']
    print(f"the request is {event}")
#Reference the dynamoDB table and retrieve data
    response = client_dynamo.get_item(
        TableName='hotelRoomAvailability',
        Key={
            'date': {
                'S': user_input_date
            }
        }
    )
    print(response['Item'])
    room_inventory_data = response['Item']
#Format the res as per requirement of Bedrock Agent (Configure Lambda to send info to Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html)
    agent = event['agent']
    actionGroup = event['actionGroup']
    api_path = event['apiPath']
    # get parameters
    get_parameters = event.get('parameters', [])
 

    response_body = {
        'application/json': {
            'body': json.dumps(room_inventory_data)
        }
    }
    print(f"\nThe response to agent is {response_body}")
    
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }
    
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    
    api_response = {
        'messageVersion': '1.0', 
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }
        
    return api_response
    print(f"\nThe final response to agent is {api_response}")