import os, json, time, jwt
from django.views import View
from django.http import JsonResponse
from bookings.models import Booking

# لاحقًا ممكن نربطه بـ AccessPass
# الآن نرجع فقط JWT + save_url

class GoogleWalletPassView(View):

    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)

            booking_id = body.get("booking_id")
            access_code = body.get("code", "N/A")

            if not booking_id:
                return JsonResponse({"error": "booking_id is required"}, status=400)

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return JsonResponse({"error": "Invalid booking_id"}, status=404)

            # بناء JWT لمحفظة Google Wallet
            token = self._build_wallet_jwt(booking, access_code)
            save_url = f"https://pay.google.com/gp/v/save/{token}"

            return JsonResponse({
                "wallet_jwt": token,
                "wallet_save_url": save_url
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def _build_wallet_jwt(self, booking, access_code):
        service_account_email = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL")
        key_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_JSON_PATH")
        issuer_id = os.getenv("GOOGLE_ISSUER_ID")
        class_suffix = os.getenv("GOOGLE_CLASS_SUFFIX")
        origins = os.getenv("WALLET_SAVE_ORIGINS", "").split()

        with open(key_path, "r") as f:
            sa = json.load(f)

        class_id = f"{issuer_id}.{class_suffix}"
        object_id = f"{issuer_id}.booking{booking.id}"

        iat = int(time.time())
        exp = iat + 3600

        payload = {
            "iss": service_account_email,
            "aud": "google",
            "typ": "savetowallet",
            "origins": origins,
            "payload": {
                "genericClasses": [
                    {
                        "id": class_id,
                        "classTemplateInfo": {
                            "cardTemplateOverride": {}
                        }
                    }
                ],
                "genericObjects": [
                    {
                        "id": object_id,
                        "classId": class_id,
                        "state": "ACTIVE",
                        "header": {
                            "defaultValue": {
                                "language": "en-US",
                                "value": "Room Access Pass"
                            }
                        },
                        "subheader": {
                            "defaultValue": {
                                "language": "en-US",
                                "value": booking.room_id
                            }
                        },
                        "barcode": {
                            "type": "QR_CODE",
                            "value": f"BOOK:{booking.id}|CODE:{access_code}"
                        },
                        "hexBackgroundColor": "#0F172A",
                        "textModulesData": [
                            {"header": "Guest", "body": booking.guest_name},
                            {"header": "Valid From", "body": booking.start_at.isoformat()},
                            {"header": "Valid To", "body": booking.end_at.isoformat()},
                        ]
                    }
                ]
            }
        }

        token = jwt.encode(
            payload,
            sa["private_key"],
            algorithm="RS256",
            headers={"kid": sa.get("private_key_id")}
        )
        return token
