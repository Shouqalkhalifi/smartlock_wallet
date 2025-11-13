from django.shortcuts import render, redirect, get_object_or_404
from bookings.models import Booking
from locks.models import SmartLock
from locks.services import provision_access_for_booking, revoke_access_for_booking

def dashboard_home(request):
    return redirect("booking_list")

def booking_list(request):
    bookings = Booking.objects.order_by("-created_at")
    return render(request, "dashboard/booking_list.html", {"bookings": bookings})

def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "dashboard/booking_detail.html", {"booking": booking})

def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    try:
        lock = SmartLock.objects.get(room_id=booking.room_id)
        access_info = provision_access_for_booking(booking, lock)

        booking.smartlock_code = access_info.get("pin_code")
        booking.wallet_save_url = access_info.get("wallet_url")
        booking.status = Booking.CONFIRMED
        booking.save()
    except Exception as e:
        return render(request, "dashboard/error.html", {"error": str(e)})

    return redirect("booking_detail", pk=pk)

def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    revoke_access_for_booking(booking)
    booking.status = Booking.CANCELLED
    booking.save()

    return redirect("booking_detail", pk=pk)
