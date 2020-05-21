import base64
import json
from typing import Any, Dict


def fetch_claims(event) -> Dict[str, Any]:
    token = event["multiValueHeaders"]["Authorization"][0]
    claims_base64 = token.split(".")[1]
    # "=====" needed to resolve padding issues
    decoded_claims = base64.urlsafe_b64decode(claims_base64 + "=====")
    return json.loads(decoded_claims)
