from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer

from locks.models import SmartLock
from locks.services import provision_access_for_booking, revoke_access_for_booking


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by("-created_at")
    serializer_class = BookingSerializer

    def get_serializer_class(self):
        return BookingCreateSerializer if self.action == "create" else BookingSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user, status=Booking.PENDING)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """
        تأكيد الحجز:
        - يربط مع SmartLock (حسب room_id)
        - ينادي Igloohome لعمل PIN مؤقت
        - ينشئ Google Wallet Pass
        """
        booking = self.get_object()

        if booking.status != Booking.PENDING:
            return Response(
                {"detail": "Booking not in pending state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lock = SmartLock.objects.get(room_id=booking.room_id)
        except SmartLock.DoesNotExist:
            return Response(
                {"detail": "No SmartLock bound to this room_id."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            access_info = provision_access_for_booking(booking, lock)

            booking.smartlock_code = access_info.get("pin_code")
            booking.wallet_save_url = access_info.get("wallet_url")
            booking.status = Booking.CONFIRMED
            booking.save()

        except Exception as e:
            return Response(
                {"detail": f"Error provisioning access: {e}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        إلغاء الحجز:
        - يلغي الكود من Igloohome
        - يعطل AccessPass
        - يحدّث حالة الحجز إلى cancelled
        """
        booking = self.get_object()

        try:
            revoke_access_for_booking(booking)
        except Exception:
            # حتى لو API فشل، نكمّل إلغاء الحجز في النظام
            pass

        booking.status = Booking.CANCELLED
        booking.save()

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
