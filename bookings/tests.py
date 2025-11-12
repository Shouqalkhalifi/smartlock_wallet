from django.utils import timezone
from django.test import TestCase
from .models import Booking

class BookingTest(TestCase):
    def test_create(self):
        start=timezone.now()+timezone.timedelta(hours=2)
        end=start+timezone.timedelta(hours=22)
        b=Booking.objects.create(guest_name="Test", room_id="101", start_at=start, end_at=end)
        self.assertEqual(b.status, "pending")
