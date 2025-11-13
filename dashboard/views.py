from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from bookings.models import Booking
from locks.models import SmartLock
from locks.services import provision_access_for_booking, revoke_access_for_booking


# -------------------------------------------------
# الصفحة الرئيسية → إعادة توجيه إلى قائمة الحجوزات
# -------------------------------------------------
def dashboard_home(request):
    return redirect("booking_list")


# -------------------------------------------------
# صفحة عرض جميع الحجوزات
# -------------------------------------------------
def booking_list(request):
    bookings = Booking.objects.order_by("-created_at")
    return render(request, "dashboard/booking_list.html", {"bookings": bookings})


# -------------------------------------------------
# صفحة تفاصيل الحجز
# -------------------------------------------------
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "dashboard/booking_detail.html", {"booking": booking})


# -------------------------------------------------
# تأكيد الحجز
# - ربط مع SmartLock
# - توليد PIN
# - إنشاء Google Wallet Pass
# -------------------------------------------------
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.status == Booking.CONFIRMED:
        messages.info(request, "هذا الحجز مؤكد مسبقاً.")
        return redirect("booking_detail", pk=pk)

    try:
        # احضار القفل الذكي حسب رقم الغرفة
        lock = SmartLock.objects.get(room_id=booking.room_id)

        # توليد: PIN + بطاقة NFC
        access_info = provision_access_for_booking(booking, lock)

        booking.smartlock_code = access_info.get("pin_code")
        booking.wallet_save_url = access_info.get("wallet_url")
        booking.status = Booking.CONFIRMED
        booking.save()

        messages.success(request, "تم تأكيد الحجز بنجاح ✔️")

    except SmartLock.DoesNotExist:
        messages.error(request, "لا يوجد قفل ذكي مرتبط بهذه الغرفة.")
        return redirect("booking_detail", pk=pk)

    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء تأكيد الحجز: {e}")
        return redirect("booking_detail", pk=pk)

    return redirect("booking_detail", pk=pk)


# -------------------------------------------------
# إلغاء الحجز
# - حذف PIN من القفل
# - تعطيل بطاقة العميل
# -------------------------------------------------
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    try:
        revoke_access_for_booking(booking)
    except Exception:
        pass  # حتى لو API فشل نستمر بالإلغاء

    booking.status = Booking.CANCELLED
    booking.save()

    messages.success(request, "تم إلغاء الحجز بنجاح ❌")
    return redirect("booking_detail", pk=pk)
