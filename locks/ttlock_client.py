import requests
from django.conf import settings


BASE = settings.TTLOCK_BASE_URL


def tt_post(path: str, data: dict):
    url = f"{BASE}{path}"
    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()


def tt_get(path: str, params: dict):
    url = f"{BASE}{path}"
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_access_token():
    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "clientSecret": settings.TTLOCK_CLIENT_SECRET,
        "grantType": "client_credentials",
    }
    return tt_post("/oauth2/token", data)


def create_pin(lock_id: str, start_ts: int, end_ts: int):
    """
    إنشاء رمز PIN مؤقت للقفل
    start_ts / end_ts بالـ milliseconds منذ 1970
    """
    token = get_access_token()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "accessToken": token["access_token"],
        "lockId": lock_id,
        "startDate": start_ts,
        "endDate": end_ts,
    }

    return tt_post("/keyboardPwd/add", data)


def delete_pin(lock_id: str, keyboard_pwd_id: int):
    token = get_access_token()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "accessToken": token["access_token"],
        "lockId": lock_id,
        "keyboardPwdId": keyboard_pwd_id,
    }

    return tt_post("/keyboardPwd/delete", data)
