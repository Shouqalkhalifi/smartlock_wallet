from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "guest_name",
        "room_id",
        "start_at",
        "end_at",
        "status",
        "smartlock_code",
        "created_at",
    )
    list_filter = ("status", "room_id")
    search_fields = ("guest_name", "guest_email", "room_id")
    readonly_fields = ("wallet_save_url", "wallet_object_id", "smartlock_code", "smartlock_key_id")
