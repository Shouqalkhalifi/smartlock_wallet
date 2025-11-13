from django.contrib import admin
from .models import SmartLock, AccessPass


@admin.register(SmartLock)
class SmartLockAdmin(admin.ModelAdmin):
    list_display = ("room_id", "name", "lock_id", "created_at")
    search_fields = ("room_id", "name", "lock_id")


@admin.register(AccessPass)
class AccessPassAdmin(admin.ModelAdmin):
    list_display = ("booking", "lock", "smartlock_pin_code", "active", "valid_from", "valid_to")
    list_filter = ("active",)
    search_fields = ("smartlock_pin_code", "wallet_object_id", "booking__guest_name")
