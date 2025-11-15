import hashlib
import requests
import time
from django.conf import settings


# ------------------------------------------------------------
# TTLOCK CONFIG — استخدام السيرفر العالمي (الحل النهائي لخطأ 10007)
# ------------------------------------------------------------

# السيرفر العالمي الصحيح (كل الحسابات الجديدة تكون هنا):
BASE_URL = "https://api.ttlock.com/v3"
OAUTH_BASE_URL = "https://api.ttlock.com"


def get_access_token():
    """
    يسحب access_token من TTLock بطريقة OAuth2 الصحيحة.
    سبب خطأ 10007 دائماً = بيانات دخول خاطئة أو استخدام سيرفر .cn
    """

    raw_password = (settings.TTLOCK_PASSWORD or "").strip()
    if not raw_password:
        raise Exception("TTLOCK_PASSWORD is empty — please set it in .env")

    # تشفير كلمة المرور كما تطلب TTLock
    password_md5 = hashlib.md5(raw_password.encode("utf-8")).hexdigest()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "clientSecret": settings.TTLOCK_CLIENT_SECRET,
        "username": settings.TTLOCK_USERNAME,
        "password": password_md5,
        "grant_type": "password",
    }

    try:
        response = requests.post(f"{OAUTH_BASE_URL}/oauth2/token", data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        raise Exception(f"TTLock OAuth request failed: {e}")

    if response.status_code != 200:
        raise Exception(
            f"TTLock Token HTTP Error {response.status_code}: {response.text[:500]}"
        )

    try:
        body = response.json()
    except ValueError:
        raise Exception(
            f"TTLock OAuth returned non-JSON body: {response.text[:500]}"
        )

    access_token = body.get("access_token")
    if not access_token:
        raise Exception(
            f"TTLock Token Error: missing access_token → {body}"
        )

    return access_token


def create_pin(lock_id: str, start_ts: int, end_ts: int):
    """
    توليد PIN وقتي Time Limited PIN
    """
    token = get_access_token()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "accessToken": token,
        "lockId": lock_id,
        "keyboardPwd": "",
        "startDate": start_ts,
        "endDate": end_ts,
        "addType": 2,             # يولد PIN تلقائياً
        "keyboardPwdType": 2,     # time-limited
        "date": int(time.time() * 1000),
    }

    try:
        response = requests.post(f"{BASE_URL}/keyboardPwd/add", data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        raise Exception(f"TTLock create_pin request failed: {e}")

    if response.status_code != 200:
        raise Exception(
            f"TTLock create_pin error {response.status_code}: {response.text}"
        )

    try:
        return response.json()
    except ValueError:
        raise Exception(
            f"TTLock create_pin returned non-JSON body: {response.text[:500]}"
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

    try:
        response = requests.post(f"{BASE_URL}/keyboardPwd/delete", data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        raise Exception(f"TTLock delete_pin request failed: {e}")

    if response.status_code != 200:
        raise Exception(
            f"TTLock delete_pin error {response.status_code}: {response.text}"
        )

    try:
        return response.json()
    except ValueError:
        raise Exception(
            f"TTLock delete_pin returned non-JSON body: {response.text[:500]}"
        )
