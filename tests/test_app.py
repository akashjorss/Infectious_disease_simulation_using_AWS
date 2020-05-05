from .context import blueprint
import pycurl
from io import BytesIO
import json

def test_app(capsys, example_fixture):
    # pylint: disable=W0612,W0613
    #test hello world
    blueprint.Blueprint.run()
    captured = capsys.readouterr()

    assert "Hello World..." in captured.out

    #test the output of lambda
    b_obj = BytesIO()
    crl = pycurl.Curl()

    # Set URL value
    crl.setopt(crl.URL, "https://dvgdt3t23b.execute-api.us-east-2.amazonaws.com/test")

    # Write bytes that are utf-8 encoded
    crl.setopt(crl.WRITEDATA, b_obj)

    # Perform a file transfer
    crl.perform()

    # End curl session
    crl.close()

    # Get the content stored in the BytesIO object (in byte characters)
    response = json.loads(b_obj.getvalue().decode('utf8'))["response"]

    # Decode the bytes stored in get_body to HTML and print the result
    #print('Output of GET request:\n%s' % response)
    assert(response == "Hello World")

def test_lambda():
    # test the output of lambda
    b_obj = BytesIO()
    crl = pycurl.Curl()

    # Set URL value
    crl.setopt(crl.URL, "https://dvgdt3t23b.execute-api.us-east-2.amazonaws.com/test")

    # Write bytes that are utf-8 encoded
    crl.setopt(crl.WRITEDATA, b_obj)

    # Perform a file transfer
    crl.perform()

    # End curl session
    crl.close()

    # Get the content stored in the BytesIO object (in byte characters)
    response = json.loads(b_obj.getvalue().decode('utf8'))["response"]

    # Decode the bytes stored in get_body to HTML and print the result
    # print('Output of GET request:\n%s' % response)
    assert (response == "Hello World")
