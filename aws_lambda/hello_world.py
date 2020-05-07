import json
import logging

logging.info("Loading function")


def hello_world_lambda_handler(event, context):
    logging.info("Received event: " + json.dumps(event, indent=2))
    logging.info("Hello World Lambda")

    body = {"response": (event["myParam"])}

    return {
        "statusCode": 200,
        "headers": {"my_header": "Hello World"},
        "body": json.dumps(body),
    }
