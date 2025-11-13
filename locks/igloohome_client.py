import requests
from django.conf import settings


class IgloohomeError(Exception):
    pass


def _request(method, path, json=None):
    base = settings.IGLOO_API_BASE_URL.rstrip("/")
    token = settings.IGLOO_API_KEY

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = f"{base}{path}"
    res = requests.request(method, url, json=json, headers=headers, timeout=15)

    if res.status_code >= 400:
        raise IgloohomeError(f"API error: {res.status_code} - {res.text}")

    return res.json()


def create_timebound_key(lock, booking):
    """
    ينشئ رمز (PIN Code) مؤقت من Igloohome للحجز.
    """
    payload = {
        "lock_id": lock.lock_id,
        "start_time": booking.start_at.isoformat(),
        "end_time": booking.end_at.isoformat(),
        "guest_name": booking.guest_name,
    }

    # مثال endpoint (يختلف حسب حسابك)
    data = _request("POST", "/locks/create-pin", json=payload)

    return {
        "key_id": data.get("key_id"),
        "pin_code": data.get("pin_code"),
    }


def revoke_igloohome_key(lock, key_id):
    """
    إلغاء كود الوصول من Igloohome.
    """
    payload = {"lock_id": lock.lock_id, "key_id": key_id}
    _request("POST", "/locks/revoke-pin", json=payload)
    return True
