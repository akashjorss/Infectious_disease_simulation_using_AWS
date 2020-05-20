import base64
import json
from typing import Any, Dict


def fetch_claims(event) -> Dict[str, Any]:
    token = event['multiValueHeaders']['Authorization'][0]
    claims_base64 = token.split(".")[1]
    decoded_claims = base64.b64decode(claims_base64)
    return json.loads(decoded_claims)
