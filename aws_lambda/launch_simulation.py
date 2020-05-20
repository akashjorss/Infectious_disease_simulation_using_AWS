import json
import logging

logging.info("Loading function")


def lambda_handler(event, context):
    logging.info("Received event: " + json.dumps(event, indent=2))
    logging.info("Hello World Lambda")

    body = {"response": (event["myParam"])}

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body),
    }
