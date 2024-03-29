import requests

CLIENT_ID = "4sinvc6tuu8rf942ehblblabp01"
CLIENT_SECRET = ""
COGNITO_TOKEN_ENDPOINT = (
    "https://meaintegration.auth.us-east-2.amazoncognito.com/oauth2/token"
)


def get_access_token():
    body = {"grant_type": "client_credentials", "scope": ["basic/basic"]}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    print("Sending Request")
    response = requests.post(
        url=COGNITO_TOKEN_ENDPOINT,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers=headers,
    )
    return response.json()


print(get_access_token())
