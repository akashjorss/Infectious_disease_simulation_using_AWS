import json
import logging
import os

import boto3
from django.db import models

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

logger = logging.getLogger(__name__)


class Leads(models.Model):

    def insert_lead(self, email, latitude, longitude, infectedFlag):

        sqs = boto3.client('sqs')

        try:
            response = sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                DelaySeconds=10,
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': email
                    },
                    'latitude': {
                        'DataType': 'String',
                        'StringValue': latitude
                    },
                    'longitude': {
                        'DataType': 'String',
                        'StringValue': longitude
                    },
                    'infectedFlag': {
                        'DataType': 'String',
                        'StringValue': infectedFlag
                    }
                },
                MessageBody=(
                    json.dumps({
                        "email": email,
                        "latitude": latitude,
                        "longitude": longitude,
                        "infectedFlag": infectedFlag,
                    })
                )
            )
        except Exception as e:
            logger.error(
                'Error adding item to sqs: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        status = response['ResponseMetadata']['HTTPStatusCode']
        if status == 200:
            if 'Attributes' in response:
                logger.error('Existing item updated to database.')
                return 409
            logger.error('New item added to database.')
        else:
            logger.error('Unknown error inserting item to database.')

        return status
