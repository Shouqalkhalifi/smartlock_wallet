from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_datetime

from bookings.models import Booking
from locks.models import Lock, AccessPass
from locks.services import provision_access_for_booking, revoke_access_for_booking


def _parse_datetime_local(value: str):
    if not value:
        return None
    return parse_datetime(value)


def dashboard_home(request):
    return render(request, "dashboard/home.html")


def booking_list(request):
    bookings = Booking.objects.order_by("-created_at")
    return render(request, "dashboard/booking_list.html", {"bookings": bookings})


def booking_create(request):
    if request.method == "POST":
        guest_name = request.POST.get("guest_name")
        room_id = request.POST.get("room_id")
        start_raw = request.POST.get("start_at")
        end_raw = request.POST.get("end_at")

        start_at = _parse_datetime_local(start_raw)
        end_at = _parse_datetime_local(end_raw)

        Booking.objects.create(
            guest_name=guest_name,
            room_id=room_id,
            start_at=start_at,
            end_at=end_at,
            status=Booking.PENDING,
        )

        messages.success(request, "تم إضافة الحجز بنجاح ✔️")
        return redirect("booking_list")

    return render(request, "dashboard/booking_create.html")


def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "POST":
        booking.guest_name = request.POST.get("guest_name")
        booking.room_id = request.POST.get("room_id")
        start_raw = request.POST.get("start_at")
        end_raw = request.POST.get("end_at")

        booking.start_at = _parse_datetime_local(start_raw)
        booking.end_at = _parse_datetime_local(end_raw)
        booking.save()

        messages.success(request, "تم تعديل الحجز ✔️")
        return redirect("booking_detail", pk=pk)

    return render(request, "dashboard/booking_edit.html", {"booking": booking})


def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "dashboard/booking_detail.html", {"booking": booking})


def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method != "POST":
        return redirect("booking_detail", pk=pk)

    if booking.status == Booking.CONFIRMED:
        messages.info(request, "الحجز مؤكد مسبقاً.")
        return redirect("booking_detail", pk=pk)

    try:
        lock = Lock.objects.get(room_id=booking.room_id)
    except Lock.DoesNotExist:
        messages.error(request, "لا يوجد قفل مربوط بهذه الغرفة.")
        return redirect("booking_detail", pk=pk)

    try:
        access_info = provision_access_for_booking(booking, lock)
        booking.status = Booking.CONFIRMED
        booking.save()

        messages.success(
            request,
            f"تم تأكيد الحجز ✔️. رمز الدخول: {access_info.get('pin_code')}",
        )
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء إنشاء رمز الدخول: {e}")

    return redirect("booking_detail", pk=pk)


def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method != "POST":
        return redirect("booking_detail", pk=pk)

    try:
        revoke_access_for_booking(booking)
    except Exception:
        pass

    booking.status = Booking.CANCELLED
    booking.save()

    messages.success(request, "تم إلغاء الحجز ❌")
    return redirect("booking_detail", pk=pk)


def locks_list(request):
    locks = Lock.objects.order_by("room_id")
    return render(request, "dashboard/locks_list.html", {"locks": locks})


# ⭐ إضافة قفل جديد
def lock_create(request):
    if request.method == "POST":
        guest_name = request.POST.get("guest_name")
        room_id = request.POST.get("room_id")
        lock_id = request.POST.get("lock_id")

        # اسم القفل يُضبط تلقائياً (يمكن لاحقاً جعله حقل مستقل في الواجهة)
        lock_name = guest_name or f"غرفة {room_id}"

        Lock.objects.create(
            room_id=room_id,
            lock_id=lock_id,
            name=lock_name,
        )

        messages.success(request, "تم إضافة القفل بنجاح ✔️")
        return redirect("locks_list")

    # تعبئة قوائم الضيوف والغرف من الحجوزات السابقة
    guests = (
        Booking.objects.exclude(guest_name="")
        .values_list("guest_name", flat=True)
        .distinct()
    )
    rooms = (
        Booking.objects.exclude(room_id="")
        .values_list("room_id", flat=True)
        .distinct()
    )

    return render(
        request,
        "dashboard/lock_create.html",
        {"guests": guests, "rooms": rooms},
    )


def wallet_home(request):
    passes = AccessPass.objects.order_by("-created_at")
    return render(request, "dashboard/wallet_list.html", {"passes": passes})
