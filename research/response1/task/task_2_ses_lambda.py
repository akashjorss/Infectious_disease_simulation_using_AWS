import json

import boto3

client = boto3.client('ses', region_name="eu-west-1")

SENDER = "Infection Alerter <snithishemircc@armyspy.com>"

# The subject line for the email.
SUBJECT = "You have been in contact with infected person"

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("You have come in contact with an infected person. Quarantine yourself for 14 days."
             )

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Contact Alert!!</h1>
  <p>You have come in contact with an infected person. Quarantine yourself for 14 days.</p>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> 
    .</p>
</body>
</html>
            """

# The character encoding for the email.
CHARSET = "UTF-8"


def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        email = body["email"]
        print(f"Sending alert to {email}")
        send_email(email)


def send_email(email: str):
    client.send_email(
        Destination={
            'ToAddresses': [
                email,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
        # If you are not using a configuration set, comment or delete the
        # following line
    )
