import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from config.settings import (
    PRODUCTHUNT_API_KEY,
    PRODUCTHUNT_API_SECRET,
)

TOKEN_URL = "https://api.producthunt.com/v2/oauth/token"


def get_access_token():
    """
    Obtain a Product Hunt OAuth access token.
    """

    payload = {
        "client_id": PRODUCTHUNT_API_KEY,
        "client_secret": PRODUCTHUNT_API_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(
        TOKEN_URL,
        json=payload,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    return data["access_token"]


if __name__ == "__main__":

    token = get_access_token()

    print("✅ Access Token Retrieved Successfully!")
    print(token[:40] + "...")