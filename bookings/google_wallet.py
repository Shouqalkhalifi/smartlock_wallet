import json
import os
from datetime import datetime
from typing import Tuple

import jwt  # PyJWT
from django.conf import settings
from django.utils import timezone


class GoogleWalletError(Exception):
    pass


def create_wallet_pass_for_booking(booking) -> Tuple[str, str]:
    """
    ينشئ JWT + save URL لبطاقة Google Wallet مرتبطة بالحجز.
    يرجّع (object_id, save_url)
    """
    key_path = settings.GOOGLE_SERVICE_ACCOUNT_KEY_JSON_PATH
    if not key_path or not os.path.exists(key_path):
        raise GoogleWalletError("Google Wallet service account key file not found")

    with open(key_path, "r", encoding="utf-8") as f:
        service_account_info = json.load(f)

    issuer_id = settings.GOOGLE_WALLET_ISSUER_ID
    class_prefix = settings.GOOGLE_WALLET_CLASS_ID_PREFIX

    audience = "google"
    scope = "https://www.googleapis.com/auth/wallet_object.issuer"
    iat = int(datetime.utcnow().timestamp())
    exp = iat + 3600  # ساعة

    class_id = f"{issuer_id}.{class_prefix}"
    object_id = f"{issuer_id}.{class_prefix}_{booking.id}"

    payload = {
        "iss": service_account_info["client_email"],
        "aud": audience,
        "typ": "savetowallet",
        "iat": iat,
        "exp": exp,
        "scope": scope,
        "payload": {
            "genericObjects": [
                {
                    "id": object_id,
                    "classId": class_id,
                    "state": "active",
                    "header": {"defaultValue": {"language": "en-US", "value": "Room Access"}},
                    "subheader": {
                        "defaultValue": {
                            "language": "en-US",
                            "value": f"Room {booking.room_id}",
                        }
                    },
                    "cardTitle": {
                        "defaultValue": {
                            "language": "en-US",
                            "value": booking.guest_name,
                        }
                    },
                    "barcode": {
                        "type": "qrCode",
                        "value": f"BOOKING-{booking.id}",
                    },
                    "validTimeInterval": {
                        "start": {
                            "dateTime": booking.start_at.astimezone(
                                timezone.utc
                            ).isoformat()
                        },
                        "end": {
                            "dateTime": booking.end_at.astimezone(
                                timezone.utc
                            ).isoformat()
                        },
                    },
                }
            ]
        },
    }

    signed_jwt = jwt.encode(
        payload,
        service_account_info["private_key"],
        algorithm="RS256",
    )

    save_url = f"https://pay.google.com/gp/v/save/{signed_jwt}"
    return object_id, save_url
