import boto3
import json
import requests
import random
from requests_aws4auth import AWS4Auth

def receiveMsgFromSqsQueue():
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/060585368592/Queue1'
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=5,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
        )
    return response

# The function return list of business id
def findRestaurantFromElasticSearch(cuisine):
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session(aws_access_key_id="",
                          aws_secret_access_key="", 
                          region_name="us-east-1").get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'search-restaurants-rjc4ohjssdb6z36tig2yjp6i5q.us-east-1.es.amazonaws.com'
    index = 'restaurants'
    url = 'https://' + host + '/' + index + '/_search'
    # i am just getting 3 buisiness id from es but its not random rn
    query = {
        "size": 1300,
        "query": {
            "query_string": {
                "default_field": "cuisine",
                "query": cuisine
            }
        }
    }
    headers = { "Content-Type": "application/json" }
    response = requests.get(url,auth=awsauth, headers=headers, data=json.dumps(query))
    res = response.json()
    noOfHits = res['hits']['total']
    hits = res['hits']['hits']
    #print(noOfHits)
    #print(hits[0]['_id'])
    buisinessIds = []
    for hit in hits:
        buisinessIds.append(str(hit['_source']['Business ID']))
    #print(len(buisinessIds))
    return buisinessIds

# function returns detail of all resturantids as a list(working)
def getRestaurantFromDb(restaurantIds):
    res = []
    client = boto3.resource('dynamodb')
    table = client.Table('yelp-restaurants')
    for id in restaurantIds:
        response = table.get_item(Key={'Business ID': id})
        res.append(response)
    return res

def getMsgToSend(restaurantDetails,message):
    noOfPeople = message['MessageAttributes']['NoOfPeople']['StringValue']
    date = message['MessageAttributes']['Date']['StringValue']
    time = message['MessageAttributes']['Time']['StringValue']
    cuisine = message['MessageAttributes']['Cuisine']['StringValue']
    separator = ', '
    resOneName = restaurantDetails[0]['Item']['name']
    resOneAdd = separator.join(restaurantDetails[0]['Item']['address'])
    resTwoName = restaurantDetails[1]['Item']['name']
    resTwoAdd = separator.join(restaurantDetails[1]['Item']['address'])
    resThreeName = restaurantDetails[2]['Item']['name']
    resThreeAdd = separator.join(restaurantDetails[2]['Item']['address'])
    msg = 'Hello! Here are my {0} restaurant suggestions for {1} people, for {2} at {3} : 1. {4}, located at {5}, 2. {6}, located at {7},3. {8}, located at {9}. Enjoy your meal!'.format(cuisine,noOfPeople,date,time,resOneName,resOneAdd,resTwoName,resTwoAdd,resThreeName,resThreeAdd)
    return msg
    
def sendSMS(msgToSend,phoneNumber):
    client = boto3.client("sns")
    # sample phone number shown PhoneNumber="+12223334444"
    client.publish(PhoneNumber = phoneNumber,Message=msgToSend)
    
def deleteMsg(receipt_handle):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/060585368592/Queue1'
    sqs.delete_message(QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
    )

def lambda_handler(event, context):
    # getting response from sqs queue
    sqsQueueResponse = receiveMsgFromSqsQueue()
    if "Messages" in sqsQueueResponse.keys():
        for message in sqsQueueResponse['Messages']:
            cuisine = message['MessageAttributes']['Cuisine']['StringValue']
            restaurantIds = findRestaurantFromElasticSearch(cuisine)
            # Assume that it returns a list of restaurantsIds
            # call some random function to select 3 from the list
            restaurantIds = random.sample(restaurantIds, 3)
            restaurantDetails = getRestaurantFromDb(restaurantIds)
            # now we have all required details to send the sms
            # now we will create the required message using the details
            msgToSend = getMsgToSend(restaurantDetails,message)
            print(msgToSend)
            # dont uncomment below line until required. There is max limit on msg
            phoneNumber = message['MessageAttributes']['PhoneNumber']['StringValue']
            if "+1" not in phoneNumber:
                phoneNumber  = '+1'+phoneNumber
            sendSMS(msgToSend,phoneNumber)
            #now delete message from queue
            receipt_handle = message['ReceiptHandle']
            deleteMsg(receipt_handle)

