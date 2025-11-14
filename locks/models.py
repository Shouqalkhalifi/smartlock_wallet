from django.db import models


class SmartLock(models.Model):
    """
    قفل ذكي من TTLock (أو مزود آخر)
    lock_id = القيمة القادمة من TTLock Cloud API
    room_id = لربطه مع غرفة في الفندق
    """
    provider = models.CharField(max_length=50, default="ttlock")
    room_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    lock_id = models.CharField(max_length=200, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_id} - {self.name}"


class AccessPass(models.Model):
    """
    كود الوصول المؤقت للقفل + بيانات بطاقة Google Wallet
    """
    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE)
    lock = models.ForeignKey(SmartLock, on_delete=models.CASCADE)

    smartlock_key_id = models.CharField(max_length=200, blank=True, null=True)
    smartlock_pin_code = models.CharField(max_length=50, blank=True, null=True)

    wallet_object_id = models.CharField(max_length=200, blank=True, null=True)
    wallet_jwt = models.TextField(blank=True, null=True)
    wallet_save_url = models.URLField(blank=True, null=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access Pass for Booking {self.booking.id}"
