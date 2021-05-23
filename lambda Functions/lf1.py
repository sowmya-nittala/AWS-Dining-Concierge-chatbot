import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---

def sendMsg(slots):
    # Send message to SQS queue
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/060585368592/Queue1'
    Attributes={
        'NoOfPeople': {
            'DataType': 'String',
            'StringValue': slots["NumberOfPeople"]
        },
        'Date': {
            'DataType': 'String',
            'StringValue': slots["DiningDate"]
        },
        'Time': {
            'DataType': 'String',
            'StringValue': slots["DiningTime"]
        },
        'PhoneNumber' : {
            'DataType': 'String',
            'StringValue': slots["PhoneNumber"]
        },
        'Cuisine': {
            'DataType': 'String',
            'StringValue': slots["Cuisine"]
        }
    }
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageAttributes=Attributes,
        MessageBody=('Testing queue')
        )
    print(response['MessageId'])

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

##########################################################################################################################
# 1. GreetingIntents
# 2. ThankYouIntent
# 3. DiningSuggestionsIntent
# 4. Build validation result
# 5. Validation methods for:
#       a. Cuisine
#       b. Number of people
#       c. date
#       d. time
#       e. city ???

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_cuisine(cuisine):
    cuisines = ['indian', 'thai', 'mediterranean', 'chinese', 'italian']
    return cuisine.lower() in cuisines

def isvalid_numberofpeople(numPeople):
    numPeople = safe_int(numPeople)
    if numPeople > 20 or numPeople < 0:
        return False
        
def isvalid_date(diningdate):
    if datetime.datetime.strptime(diningdate, '%Y-%m-%d').date() <= datetime.date.today():
        return False

def isvalid_time(diningdate, diningtime):
    if datetime.datetime.strptime(diningdate, '%Y-%m-%d').date() == datetime.date.today():
        if datetime.datetime.strptime(diningtime, '%H:%M').time() <= datetime.datetime.now().time():
            return False

def validate_dining_suggestion(cuisine, numPeople, diningdate, diningtime):
    if cuisine is not None:
        if not isvalid_cuisine(cuisine):
            return build_validation_result(False, 'Cuisine', 'Cuisine not available. Please try another.')
    
    if numPeople is not None:
        if not isvalid_numberofpeople(numPeople):
            return build_validation_result(False, 'NumberOfPeople', 'Maximum 20 people allowed. Try again')
            
    if diningdate is not None:
        if not isvalid_date(diningdate):
            return build_validation_result(False, 'diningdate', 'Please enter valid date')
    
    if diningtime is not None and diningdate is not None:
        if not isvalid_time(diningdate, diningtime):
            return build_validation_result(False, 'diningtime', 'Please enter valid time')

            
            

    return build_validation_result(True, None, None)





def greetings(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText',
                'content': 'Hi there, how can I help?'}
        }
    }

def thank_you(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText',
                'content': 'You are welcome!'}
        }
    }

def dining_suggestions(intent_request):
    slots = intent_request['currentIntent']['slots']
    cuisine = slots["Cuisine"]
    numPeople = slots["NumberOfPeople"]
    diningdate = slots["DiningDate"]
    diningtime = slots["DiningTime"]
    location = slots["Location"]
    phonenumber = slots["PhoneNumber"]
    
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_dining_suggestion(cuisine, numPeople, diningdate, diningtime)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
    
        if intent_request[
                'sessionAttributes'] is not None:
                output_session_attributes = intent_request['sessionAttributes']
        else:
            output_session_attributes = {}
    
        return delegate(output_session_attributes, intent_request['currentIntent']['slots'])
            
    # after fulfilment calling sqs
    sendMsg(slots)
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you! You will recieve suggestion shortly'})
    



# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggestions(intent_request)
    elif intent_name == 'GreetingIntents':
        return greetings(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
