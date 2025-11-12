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
        return BookingCreateSerializer if self.action=="create" else BookingSerializer

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        booking=self.get_object()
        if booking.status != Booking.PENDING:
            return Response({"detail":"Booking not in pending state"}, status=400)
        # اختاري القفل حسب room_id
        try:
            lock=SmartLock.objects.get(room_id=booking.room_id)
        except SmartLock.DoesNotExist:
            return Response({"detail":"No lock bound to this room"}, status=404)

        provision_access_for_booking(booking, lock)
        booking.status=Booking.CONFIRMED; booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking=self.get_object()
        revoke_access_for_booking(booking)
        booking.status=Booking.CANCELLED; booking.save()
        return Response(BookingSerializer(booking).data, status=200)
