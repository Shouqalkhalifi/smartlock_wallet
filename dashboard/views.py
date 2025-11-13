from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from bookings.models import Booking
from locks.models import SmartLock
from locks.services import provision_access_for_booking, revoke_access_for_booking


# لوحة الموظف
def dashboard_home(request):
    return render(request, "dashboard/home.html")


# -----------------------------
# قائمة الحجوزات
# -----------------------------
def booking_list(request):
    bookings = Booking.objects.order_by("-created_at")
    return render(request, "dashboard/booking_list.html", {"bookings": bookings})


# -----------------------------
# إنشاء حجز جديد
# -----------------------------
def booking_create(request):
    if request.method == "POST":
        guest_name = request.POST.get("guest_name")
        room_id = request.POST.get("room_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        Booking.objects.create(
            guest_name=guest_name,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date,
        )

        messages.success(request, "تم إضافة الحجز بنجاح ✔️")
        return redirect("booking_list")

    return render(request, "dashboard/booking_create.html")


# -----------------------------
# تعديل الحجز
# -----------------------------
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "POST":
        booking.guest_name = request.POST.get("guest_name")
        booking.room_id = request.POST.get("room_id")
        booking.start_date = request.POST.get("start_date")
        booking.end_date = request.POST.get("end_date")
        booking.save()

        messages.success(request, "تم تعديل الحجز ✔️")
        return redirect("booking_detail", pk=pk)

    return render(request, "dashboard/booking_edit.html", {"booking": booking})


# -----------------------------
# تفاصيل الحجز
# -----------------------------
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "dashboard/booking_detail.html", {"booking": booking})


# -----------------------------
# تأكيد الحجز (نسخة محمّكة بدون API)
# -----------------------------
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.status == Booking.CONFIRMED:
        messages.info(request, "الحجز مؤكد مسبقاً.")
        return redirect("booking_detail", pk=pk)

    # محاكاة إنشاء PIN
    booking.smartlock_code = "123456"
    booking.wallet_save_url = "https://example.com/wallet-pass"
    booking.status = Booking.CONFIRMED
    booking.save()

    messages.success(request, "تم تأكيد الحجز بنجاح ✔️ (محاكاة)")
    return redirect("booking_detail", pk=pk)


# -----------------------------
# إلغاء الحجز
# -----------------------------
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    booking.status = Booking.CANCELLED
    booking.save()

    messages.success(request, "تم إلغاء الحجز ❌")
    return redirect("booking_detail", pk=pk)
