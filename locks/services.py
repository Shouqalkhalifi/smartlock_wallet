from .models import AccessPass
from bookings.models import Booking
from .igloohome_client import create_timebound_key, revoke_igloohome_key
from bookings.google_wallet import create_wallet_pass_for_booking


def provision_access_for_booking(booking: Booking, lock):
    """
    1) إنشاء PIN مؤقت من Igloohome
    2) إنشاء بطاقة Google Wallet
    3) حفظ AccessPass
    """
    # 1) Igloohome
    key_data = create_timebound_key(lock, booking)

    # 2) Google Wallet
    object_id, save_url = create_wallet_pass_for_booking(booking)

    # 3) إنشاء AccessPass
    AccessPass.objects.create(
        booking=booking,
        lock=lock,
        smartlock_key_id=key_data["key_id"],
        smartlock_pin_code=key_data["pin_code"],
        wallet_object_id=object_id,
        wallet_save_url=save_url,
        valid_from=booking.start_at,
        valid_to=booking.end_at,
    )

    return {
        "pin_code": key_data["pin_code"],
        "wallet_url": save_url,
    }


def revoke_access_for_booking(booking: Booking):
    """
    إلغاء الكود من Igloohome + تعطيل AccessPass
    """
    try:
        ap = AccessPass.objects.get(booking=booking, active=True)
    except AccessPass.DoesNotExist:
        return True

    # إلغاء الكود من Igloohome
    revoke_igloohome_key(ap.lock, ap.smartlock_key_id)

    # تعطيل الـ AccessPass
    ap.active = False
    ap.save()

    return True
