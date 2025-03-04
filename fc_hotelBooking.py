import json
import boto3 #python aws sdk 
import uuid #random id generator
import os #operating system


client_dynamodb = boto3.client('dynamodb')
def lambda_handler(event, context):
    # TODO implement
    print(f"The request is {event}")
    #input_data = event 
    input_data = event['requestBody']['content']['application/json']['properties']
    print(f"Input data is {input_data}")

    for item in input_data: 
        if item['name'] == 'guestName':
            guestName = item['value']
        elif item['name'] == 'checkInDate':
            checkInDate = item['value']
        elif item['name'] == 'numberOfNights':
            numberOfNights = item['value']
        elif item['name'] == 'roomType':
            roomType = item['value']

    print(f"Guest name is {guestName}")
    print(f"Check in date is {checkInDate}")
    print(f"Number of nights is {numberOfNights}")
    print(f"Room type is {roomType}")
    # Store user input 
### Important need to modify the request data from user sending


# # Retrieve data from event -checkInDate roomType guestName numberOfNights
#     guestName = input_data['guestName']
#     checkInDate = input_data['checkInDate']
#     numberOfNights = input_data['numberOfNights']
#     roomType = input_data['roomType']
#     print(f"Guest name is {guestName}")

# Get room availability from HotelRoomAvailability Table in Dynamo DB using get_item
    response = client_dynamodb.get_item(TableName='hotelRoomAvailability', Key={'date': {'S': checkInDate}})
    print(f"Response from DynamoDB is {response}")
    roomAvailable = response['Item']
    print(f"Room available is {roomAvailable}")

# Get room availability for SeaView Room and GardenView Room convert to Integer to Caculate Rooms are Available
    current_gardenViewRoom = int(roomAvailable['gardenView']['S'])
    current_seaViewRoom = int(roomAvailable['seaView']['S'])
    print(type(current_gardenViewRoom))
    print(type(current_seaViewRoom))
    print(f"Current Garden View Room is {current_gardenViewRoom}")
    print(f"Current Sea View Room is {current_seaViewRoom}")
# If roomAvailable is 0 sending a notify to the user that no rooms are available
    if current_gardenViewRoom == 0 and current_seaViewRoom == 0 :
        response = {
            'statusCode': 200,
            'body': json.dumps('No rooms available for the specified date, you can choose another date')
        }
        print(f"Response is {response}")
        return response
    elif  int(numberOfNights) > current_gardenViewRoom and int(numberOfNights) > current_seaViewRoom:
        response = {
            'statusCode': 200,
            'body': json.dumps('Out of slot rooms available for the specified date, you can reduce you numOfNights')
        }
        print(f"Response is {response}")
        return response

# Generate unique booking ID to store in Dynamo DB along with information user provided and response to user
    else:
        bookingId = str(uuid.uuid4())
        print(f"Booking ID is {bookingId}")
        #using put_item to modify inserting to Dynamo D
        response_dynamodb = client_dynamodb.put_item(TableName='hotelRoomBookingTable', Item={'bookingId': {'S': bookingId}, 'guestName': {'S': guestName}, 'checkInDate': {'S': checkInDate}, 'numberOfNights': {'S': numberOfNights}, 'roomType': {'S': roomType}})     
      
# Print bookingId after booking successfully
    print(f"Booking ID is {bookingId}")
# Configure Lambda event to send response to Bedrock Agent Expected https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
    agent = event['agent']
    actionGroup = event['actionGroup']
    api_path = event['apiPath']
   
    # post parameters
    post_parameters = event['requestBody']['content']['application/json']['properties']

    response_body = {
        'application/json': {
            'body': json.dumps(bookingId)
        }
    }
    
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