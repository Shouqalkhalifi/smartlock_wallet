import hashlib
import requests
import time
from django.conf import settings


# نثبت دومين TTLock الرسمي (.com.cn) لمسارات v3 حتى لا يتأثر بخطأ في متغير البيئة
BASE_URL = "https://api.ttlock.com.cn/v3"  # قاعدة روابط v3 (keyboardPwd, locks, ...)
OAUTH_BASE_URL = "https://api.ttlock.com"  # OAuth2 لا يعمل تحت /v3


def get_access_token():
    """
    سحب توكن TTLock باستخدام OAuth2
    """
    raw_password = settings.TTLOCK_PASSWORD or ""
    password_md5 = hashlib.md5(raw_password.encode("utf-8")).hexdigest()

    data = {
        "clientId": settings.TTLOCK_CLIENT_ID,
        "clientSecret": settings.TTLOCK_CLIENT_SECRET,
        "username": settings.TTLOCK_USERNAME,
        "password": password_md5,
        "grant_type": "password",
    }

    response = requests.post(f"{OAUTH_BASE_URL}/oauth2/token", data=data)

    if response.status_code != 200:
        raise Exception(
            "TTLock Token Error HTTP "
            f"(status={response.status_code}, url={response.request.url}, payload={data}): "
            f"{response.text[:500]}"
        )

    try:
        body = response.json()
    except ValueError:
        raise Exception(
            f"TTLock Token Error: non‑JSON response body: {response.text[:500]}"
        )

    access_token = body.get("access_token")
    if not access_token:
        # نرفع الخطأ مع الجسم الكامل لمعرفة errcode/errmsg من TTLock
        raise Exception(f"TTLock Token Error: missing access_token in response: {body}")

    return access_token


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
        ct = response.headers.get("Content-Type", "")
        raise Exception(
            "TTLock create_pin HTTP error "
            f"(status={response.status_code}, content_type={ct}, "
            f"url={response.request.url}, payload={data}): "
            f"{response.text[:500]}"
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
