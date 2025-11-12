import os, time, json, jwt, requests, datetime as dt
from django.utils import timezone
from .models import AccessPass
from bookings.models import Booking

TTLOCK_OAUTH_URL="https://api.sciener.com/oauth2/token"          # OAuth (Resource Owner Password) :contentReference[oaicite:5]{index=5}
TTLOCK_ADD_PWD_URL="https://api.sciener.com/v3/keyboardPwd/add"   # إضافة كود للباب :contentReference[oaicite:6]{index=6}
WALLET_SAVE_URL_PREFIX="https://pay.google.com/gp/v/save/"        # رابط الحفظ :contentReference[oaicite:7]{index=7}

def _now_ms():
    return int(time.time()*1000)

class SmartLockAdapter:
    def create_timebound_code(self, lock, start_at, end_at)->str:
        raise NotImplementedError
    def revoke(self, lock, code:str):
        return True

class TTLockAdapter(SmartLockAdapter):
    def _get_access_token(self):
        data={
            "client_id":os.getenv("TTLOCK_CLIENT_ID"),
            "client_secret":os.getenv("TTLOCK_CLIENT_SECRET"),
            "username":os.getenv("TTLOCK_USERNAME"),
            "password":os.getenv("TTLOCK_PASSWORD")
        }
        r=requests.post(TTLOCK_OAUTH_URL, data=data, timeout=15)
        r.raise_for_status()
        return r.json()["access_token"]

    def create_timebound_code(self, lock, start_at, end_at)->str:
        token=self._get_access_token()
        payload={
            "clientId":os.getenv("TTLOCK_CLIENT_ID"),
            "accessToken":token,
            "lockId":int(lock.external_id),
            "keyboardPwd":"",        # يختار السيرفر الرمز
            "startDate":int(start_at.timestamp()*1000),
            "endDate":int(end_at.timestamp()*1000),
            "date":_now_ms(),
        }
        r=requests.post(TTLOCK_ADD_PWD_URL, data=payload, timeout=20)
        r.raise_for_status()
        data=r.json()
        # الـ API يرجع الـ ID ويمكن استرجاع الكود لاحقًا إن لزم (بعض الطرازات تُرجع الكود مباشرة) :contentReference[oaicite:8]{index=8}
        return str(data.get("keyboardPwd","")) or str(data.get("keyboardPwdId"))

def get_adapter_for(lock_vendor:str)->SmartLockAdapter:
    if lock_vendor=="TTLOCK":
        return TTLockAdapter()
    # IGLOO/AQARA: ادمجي SDK/Cloud لاحقًا بنفس الواجهة. :contentReference[oaicite:9]{index=9}
    return SmartLockAdapter()

def _wallet_jwt_for_booking(booking:Booking, access_code:str, object_suffix:str)->str:
    # بناء JWT للـ Generic Pass (class & object) مع Origins
    issuer_id=os.getenv("GOOGLE_ISSUER_ID")
    class_id=f"{issuer_id}.{os.getenv('GOOGLE_CLASS_SUFFIX')}"
    object_id=f"{issuer_id}.{object_suffix}"

    service_account_email=os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL")
    sa_env=os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_JSON")
    if sa_env:
        sa=json.loads(sa_env)
    else:
        key_path=os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_JSON_PATH")
        with open(key_path,"r") as f:
            sa=json.load(f)

    iat=int(time.time())
    exp=iat+3600
    origins=os.getenv("WALLET_SAVE_ORIGINS","").split()

    payload={
      "iss": service_account_email,
      "aud": "google",
      "typ": "savetowallet",
      "origins": origins,                           # مطلوبة لزر الحفظ في الويب :contentReference[oaicite:10]{index=10}
      "payload": {
        "genericClasses": [
          {"id": class_id, "classTemplateInfo": {"cardTemplateOverride": {}}}
        ],
        "genericObjects": [
          {
            "id": object_id,
            "classId": class_id,
            "state": "ACTIVE",
            "header": {"defaultValue": {"language":"en-US","value": "Room Access Pass"}},
            "subheader": {"defaultValue": {"language":"en-US","value": booking.room_id}},
            "barcode": {"type":"QR_CODE", "value": f"BOOK:{booking.id}|CODE:{access_code}"},
            "hexBackgroundColor": "#0F172A",
            "logo": {"sourceUri":{"uri":"https://your-admin.example.com/logo.png"}},
            "textModulesData": [
              {"header":"Guest","body":booking.guest_name},
              {"header":"Valid From","body":booking.start_at.isoformat()},
              {"header":"Valid To","body":booking.end_at.isoformat()},
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

def provision_access_for_booking(booking:Booking, lock):
    adapter=get_adapter_for(lock.vendor)
    # 1) كود زمني للقفل
    code=adapter.create_timebound_code(lock, booking.start_at, booking.end_at)
    # 2) JWT لحفظ البطاقة في Google Wallet
    object_suffix=f"booking{booking.id}"
    token=_wallet_jwt_for_booking(booking, code or "N/A", object_suffix)
    save_url=WALLET_SAVE_URL_PREFIX + token  # https://pay.google.com/gp/v/save/{JWT} :contentReference[oaicite:11]{index=11}

    AccessPass.objects.create(
        booking=booking, lock=lock,
        code=code, wallet_jwt=token, wallet_object_id=f"{os.getenv('GOOGLE_ISSUER_ID')}.{object_suffix}",
        valid_from=booking.start_at, valid_to=booking.end_at, is_active=True
    )
    return {"code":code, "wallet_save_url": save_url}

def revoke_access_for_booking(booking:Booking):
    # هنا نُلغي على مستوى القفل (حذف/تعطيل الكود) + نعطّل الـ AccessPass
    for ap in AccessPass.objects.filter(booking=booking, is_active=True):
        ap.is_active=False; ap.save()
    return True
