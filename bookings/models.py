from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField(blank=True, null=True)  # ✅ يقبل بدون قيمة
    room_id = models.CharField(max_length=50)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    def __str__(self):
        return f"Booking {self.id} for {self.guest_name}"
