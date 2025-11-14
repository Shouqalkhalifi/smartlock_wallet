from django.contrib import admin
from .models import Lock, AccessPass


@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    list_display = ("room_id", "name", "lock_id", "provider", "created_at")
    search_fields = ("room_id", "name", "lock_id")


@admin.register(AccessPass)
class AccessPassAdmin(admin.ModelAdmin):
    list_display = ("booking", "lock", "valid_from", "valid_to", "active")
    search_fields = ("booking__guest_name", "lock__room_id")
    list_filter = ("active",)
