from django.db import models
from bookings.models import Booking

class SmartLock(models.Model):
    VENDORS = [
        ("TTLOCK", "TTLock"),
        ("AQARA", "Aqara"),
        ("IGLOO", "Igloohome"),
    ]

    name = models.CharField(max_length=100)
    vendor = models.CharField(max_length=20, choices=VENDORS, default="TTLOCK")
    room_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    external_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Lock ID from vendor API"
    )

    location = models.CharField(max_length=255, default="Unknown Location")

    def __str__(self):
        return f"{self.name} ({self.vendor})"


class AccessPass(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    lock = models.ForeignKey(SmartLock, on_delete=models.CASCADE)

    code = models.CharField(max_length=255, blank=True, null=True)
    wallet_jwt = models.TextField(blank=True, null=True)
    wallet_object_id = models.CharField(max_length=255, blank=True, null=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access for Booking {self.booking.id}"
