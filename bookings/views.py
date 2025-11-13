from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer

from locks.models import SmartLock
from locks.services import provision_access_for_booking, revoke_access_for_booking


# -------------------------------------------------
# 🟣 Dashboard (واجهة لوحة الحجوزات)
# -------------------------------------------------
def dashboard(request):
    bookings = Booking.objects.all().order_by("-created_at")

    if request.method == "POST":
        guest_name = request.POST.get("guest_name")
        room_id = request.POST.get("room_id")
        start_at = request.POST.get("start_at")
        end_at = request.POST.get("end_at")

        Booking.objects.create(
            guest_name=guest_name,
            room_id=room_id,
            start_at=start_at,
            end_at=end_at,
            status=Booking.PENDING,
        )
        return redirect("dashboard")

    return render(request, "dashboard.html", {"bookings": bookings})


# -------------------------------------------------
# 🟣 Booking API (للـ mobile أو الأنظمة الخارجية)
# -------------------------------------------------
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by("-created_at")
    serializer_class = BookingSerializer

    def get_serializer_class(self):
        return BookingCreateSerializer if self.action == "create" else BookingSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user, status=Booking.PENDING)

    # -------------------------------------------------
    # 🟢 تأكيد الحجز (Generate PIN + Google Wallet)
    # -------------------------------------------------
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):

        booking = self.get_object()

        if booking.status != Booking.PENDING:
            return Response(
                {"detail": "الحجز ليس في حالة انتظار (pending)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔍 ابحث عن SmartLock مربوط بالغرفة
        try:
            lock = SmartLock.objects.get(room_id=booking.room_id)
        except SmartLock.DoesNotExist:
            return Response(
                {"detail": "لا يوجد قفل (SmartLock) مربوط بهذه الغرفة."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 🔐 إنشاء الـ PIN + Wallet Pass
        try:
            access_info = provision_access_for_booking(booking, lock)

            booking.smartlock_code = access_info.get("pin_code")
            booking.wallet_save_url = access_info.get("wallet_url")
            booking.status = Booking.CONFIRMED
            booking.save()

        except Exception as e:
            return Response(
                {"detail": f"حدث خطأ أثناء إنشاء رمز الدخول: {e}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    # -------------------------------------------------
    # 🔴 إلغاء الحجز (Cancel PIN + Disable Wallet)
    # -------------------------------------------------
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):

        booking = self.get_object()

        try:
            revoke_access_for_booking(booking)
        except Exception:
            pass  # حتى لو API فشل، نستمر بالإلغاء

        booking.status = Booking.CANCELLED
        booking.save()

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
