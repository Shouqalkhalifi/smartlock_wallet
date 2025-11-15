import requests

url = "https://api.ttlock.com/v3/oauth2/token"

data = {
    "clientId": "068ed449f3074fa5a8effd5c9fc49ed1",
    "clientSecret": "cf6f87bbef0308efa9e2b788334ad57b",
    "username": "kh080dddd@gmail.com",
    "password": "5xFM7kDckx4Q9H.",
    "grantType": "password",
}

res = requests.post(url, data=data)

print("STATUS:", res.status_code)
print("RESPONSE:", res.text)
