import json

import boto3
from pytest_mock import MockFixture
from aws_lambda.launch_simulation import lambda_handler


def test_lambda(mocker: MockFixture):
    event = {
        "multiValueHeaders": {
            "Authorization": [
                "Bearer eyJraWQiOiJUXC8wY281Qml6S0ZVTnlCQVZBa0VuY242SnJXVTVjNkV2eUk4RWZ6RENrWT0iLCJhbGciOiJSUzI1NiJ9"
                ".eyJzdWIiOiI5YmU0ZDYwYS01YTY0LTQ3M2QtYmU5NS1kYjAyNzZiODE1ZDAiLCJhdWQiOiIybWpzOGMzM3A3cXZrMW1ydjh0OGlqZGJqbSIsImV2ZW50X2lkIjoiYmRhZGRkNTEtMzY0My00MjNiLWJhNzYtYWZlY2EyZGUxM2Q2IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE1ODk5NjY5NDksImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2NOeEdxTTZRZiIsImNvZ25pdG86dXNlcm5hbWUiOiJlYXJuIiwiZXhwIjoxNTg5OTcwNTQ5LCJpYXQiOjE1ODk5NjY5NDl9.Vj0clXW9njSH84xmbVyqA49tJwUXpxH3Lyq4IBMAfvjVbbWmCQnGt1zwZcnctoeSDnhjEEcXvBW73KioVWZl7vI4gxLIGZ5h4DINVaqv_6CCQgzn_vluCEaCVFDHTvJauKJIgeMIOq9R071u6e4IpLQsLt_BWeMtwvJLvtjwNUJ3gG85A28Ka1usdwPY0g6oxZp4zS4QQ8J1vMHL04SsnwZCGnaLeQM-At7OTB8XJ6jeVh-vj8gdRR_Wd7gEphM826Td3lg8VuYfrHBiGtBh48FmazCqNFWUP9PHyHfK15OL8Z7Kt3zTwnexYe60qRRMkzZdPeamW6rsE_z1AwiDMA"
            ]}
    }
    mock_boto = mocker.patch("boto3.client")
    response = lambda_handler(event, None)
    response_body = response["body"]
    response_header = response["headers"]
    response_body = json.loads(response_body)["simulation_id"]
    assert mock_boto.call_count == 1
    assert mock_boto.call_args[0] == ("emr", )
    assert mock_boto.call_args[1] == {"region_name": "us-east-1"}
    assert response_body != ""
    assert response_header["Access-Control-Allow-Origin"] == "*"
