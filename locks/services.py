from django.utils import timezone

from bookings.models import Booking
from bookings.google_wallet import create_wallet_pass_for_booking
from .models import SmartLock, AccessPass
from .ttlock_client import create_pin, delete_pin


def provision_access_for_booking(booking: Booking, lock: SmartLock) -> dict:
    """
    إنشاء PIN مؤقت للقفل + بطاقة Google Wallet وربطه بالحجز
    """
    if booking.start_at >= booking.end_at:
        raise ValueError("Invalid booking time range")

    # تحويل إلى timestamps بالـ milliseconds (حسب TTLock)
    start_ts = int(booking.start_at.timestamp() * 1000)
    end_ts = int(booking.end_at.timestamp() * 1000)

    # استدعاء TTLock لإنشاء PIN
    pin_response = create_pin(lock.lock_id, start_ts, end_ts)

    # NOTE: يجب التأكد من شكل الـ response الحقيقي من TTLock
    # غالباً: keyboardPwdId + keyboardPwd
    if pin_response.get("errcode") not in (0, None):
        raise RuntimeError(f"TTLock error: {pin_response}")

    key_id = pin_response.get("keyboardPwdId") or pin_response.get("passwordId")
    pin_code = pin_response.get("keyboardPwd") or pin_response.get("password")

    if not key_id or not pin_code:
        raise RuntimeError(f"Invalid response from TTLock: {pin_response}")

    # إنشاء بطاقة Google Wallet
    object_id, save_url = create_wallet_pass_for_booking(booking)

    access_pass = AccessPass.objects.create(
        booking=booking,
        lock=lock,
        smartlock_key_id=str(key_id),
        smartlock_pin_code=str(pin_code),
        wallet_object_id=object_id,
        wallet_save_url=save_url,
        valid_from=booking.start_at,
        valid_to=booking.end_at,
        active=True,
    )

    # تحديث بعض الحقول في Booking لسهولة العرض
    booking.smartlock_key_id = access_pass.smartlock_key_id
    booking.smartlock_code = access_pass.smartlock_pin_code
    booking.wallet_object_id = access_pass.wallet_object_id
    booking.wallet_save_url = access_pass.wallet_save_url
    booking.save(update_fields=[
        "smartlock_key_id",
        "smartlock_code",
        "wallet_object_id",
        "wallet_save_url",
    ])

    return {
        "pin_code": pin_code,
        "wallet_url": save_url,
    }


def revoke_access_for_booking(booking: Booking) -> bool:
    """
    إلغاء صلاحية الوصول المرتبطة بحجز معيّن (TTLock + AccessPass)
    """
    try:
        access_pass = AccessPass.objects.get(booking=booking, active=True)
    except AccessPass.DoesNotExist:
        return True

    # استدعاء TTLock لإلغاء الـ PIN
    try:
        delete_pin(access_pass.lock.lock_id, access_pass.smartlock_key_id)
    except Exception:
        # لا نوقف العملية حتى لو فشل الـ API، لكن يفضّل تسجيل الخطأ في logging
        pass

    access_pass.active = False
    access_pass.save(update_fields=["active"])

    # ممكن كذلك مسح الكود من الحجز لو حابة
    booking.smartlock_code = None
    booking.smartlock_key_id = None
    booking.save(update_fields=["smartlock_code", "smartlock_key_id"])

    return True
