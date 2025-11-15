import requests
import time
from django.conf import settings


BASE_URL = settings.TTLOCK_BASE_URL  # قاعدة روابط v3 (keyboardPwd, locks, ...)
OAUTH_BASE_URL = "https://api.ttlock.com.cn"  # OAuth2 لا يعمل تحت /v3


def get_access_token():
    """
    سحب توكن TTLock باستخدام OAuth2
    """
    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "clientSecret": settings.TTLOCK_CLIENT_SECRET,
        "username": settings.TTLOCK_USERNAME,
        "password": settings.TTLOCK_PASSWORD,
        "grant_type": "password",
    }

    # ملاحظة: حسب توثيق TTLock، مسار التوكن لا يحتوي /v3
    response = requests.post(f"{OAUTH_BASE_URL}/oauth2/token", data=data)

    if response.status_code != 200:
        raise Exception(f"TTLock Token Error: {response.text}")

    return response.json().get("access_token")


def create_pin(lock_id: str, start_ts: int, end_ts: int):
    """
    إنشاء رقم سري (PIN) للقفل
    """
    token = get_access_token()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "accessToken": token,
        "lockId": lock_id,
        "keyboardPwd": "",          # نخلي السيرفر يولّد الرمز
        "startDate": start_ts,
        "endDate": end_ts,
        "addType": 2,               # ★ مهم: خلي TTLock يولّد الـ PIN
        "keyboardPwdType": 2,       # time‑limited
        "date": int(time.time() * 1000),
    }

    response = requests.post(f"{BASE_URL}/keyboardPwd/add", data=data)

    # تأكيد أن الاستجابة ناجحة ومن نوع JSON
    if response.status_code != 200:
        raise Exception(
            f"TTLock create_pin error (status {response.status_code}): {response.text}"
        )

    try:
        return response.json()
    except ValueError:
        # يحدث عندما لا يكون الرد JSON صالح
        raise Exception(
            f"TTLock create_pin returned non‑JSON body: {response.text[:500]}"
        )


def delete_pin(lock_id: str, keyboard_pwd_id: str):
    """
    حذف PIN من القفل
    """
    token = get_access_token()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "accessToken": token,
        "lockId": lock_id,
        "keyboardPwdId": keyboard_pwd_id,
        "date": int(time.time() * 1000),
    }

    response = requests.post(f"{BASE_URL}/keyboardPwd/delete", data=data)

    if response.status_code != 200:
        raise Exception(
            f"TTLock delete_pin error (status {response.status_code}): {response.text}"
        )

    try:
        return response.json()
    except ValueError:
        raise Exception(
            f"TTLock delete_pin returned non‑JSON body: {response.text[:500]}"
        )
