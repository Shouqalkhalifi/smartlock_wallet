from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Booking(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
        (EXPIRED, "Expired"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField(blank=True, null=True)

    room_id = models.CharField(max_length=50)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    wallet_object_id = models.CharField(max_length=200, blank=True, null=True)
    wallet_save_url = models.URLField(blank=True, null=True)

    smartlock_code = models.CharField(max_length=100, blank=True, null=True)
    smartlock_key_id = models.CharField(max_length=100, blank=True, null=True)

    def is_active(self) -> bool:
        now = timezone.now()
        return self.status == self.CONFIRMED and self.start_at <= now <= self.end_at

    def __str__(self) -> str:
        return f"Booking {self.id} for {self.guest_name} @ room {self.room_id}"
