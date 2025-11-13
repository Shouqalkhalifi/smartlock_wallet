from rest_framework import serializers
from .models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["guest_name", "guest_email", "room_id", "start_at", "end_at"]

    def validate(self, data):
        if data["end_at"] <= data["start_at"]:
            raise serializers.ValidationError("end_at must be after start_at")
        return data


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "guest_name",
            "guest_email",
            "room_id",
            "start_at",
            "end_at",
            "status",
            "wallet_save_url",
            "wallet_object_id",
            "smartlock_code",
            "smartlock_key_id",
            "created_at",
        ]
