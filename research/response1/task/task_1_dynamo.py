# !/usr/bin/python3 -u
import json
from typing import Dict, List

import boto3

sqs = boto3.client('sqs', region_name="eu-west-1")
dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")

queue_url = 'https://sqs.eu-west-1.amazonaws.com/787949316120/MyQueue'
alert_queue = 'https://sqs.eu-west-1.amazonaws.com/787949316120/InfectionAlertQueue'


def add_alert(infected: str, people_in_same_location: List[Dict[str, str]]):
    if infected == "Yes":
        alerted = []
        for person in people_in_same_location:
            if person["email"] not in alerted:
                sqs.send_message(QueueUrl=alert_queue,
                                 DelaySeconds=10,
                                 MessageBody=(json.dumps({
                                     "email":
                                     person["email"],
                                 })))
                alerted.append(person["email"])


def update_dynamo(message: Dict[str, str]):
    key = f"lat:{message['latitude']}+lon:{message['longitude']}"
    table = dynamodb.Table("spread_tracking")
    response = table.get_item(Key={'location': key})
    data = [{
        "email": message["email"],
        "infectedFlag": message["infectedFlag"]
    }]
    if 'Item' in response:
        people_in_same_location = response['Item']['data']
        add_alert(message["infectedFlag"], people_in_same_location)
        data = data + people_in_same_location
    table.put_item(Item={"location": key, "data": data})


def poll():
    while True:
        messages = sqs.receive_message(QueueUrl=queue_url,
                                       MaxNumberOfMessages=1,
                                       WaitTimeSeconds=20)

        if 'Messages' in messages and messages['Messages']:
            message = messages['Messages'][0]
            print(message['Body'])
            update_dynamo(json.loads(message['Body']))
            sqs.delete_message(QueueUrl=queue_url,
                               ReceiptHandle=message['ReceiptHandle'])


if __name__ == '__main__':
    poll()
