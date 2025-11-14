from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import render

from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer


def dashboard(request):
    return render(request, "dashboard/bookings.html")


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by("-id")
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer
