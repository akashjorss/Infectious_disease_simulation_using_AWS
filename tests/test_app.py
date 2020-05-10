import json

from aws_lambda.hello_world import hello_world_lambda_handler
from .context import blueprint


def test_app(capsys, example_fixture):
    # pylint: disable=W0612,W0613
    # test hello world
    blueprint.Blueprint.run()
    captured = capsys.readouterr()

    assert "Hello World..." in captured.out


def test_lambda():
    response = hello_world_lambda_handler(
        {"myParam": "Hello World from AWS lambda"}, None)
    response_body = response["body"]
    response_body = json.loads(response_body)["response"]
    assert response_body == "Hello World from AWS lambda"
