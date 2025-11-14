from rest_framework import serializers
from .models import Booking
import pytz

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["guest_name", "guest_email", "room_id", "start_at", "end_at"]

    def validate(self, data):
        riyadh = pytz.timezone("Asia/Riyadh")

        start = data["start_at"]
        end = data["end_at"]

        if start.tzinfo is None:
            start = riyadh.localize(start)
        if end.tzinfo is None:
            end = riyadh.localize(end)

        if end <= start:
            raise serializers.ValidationError("end_at must be after start_at")

        data["start_at"] = start
        data["end_at"] = end

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
        read_only_fields = (
            "status",
            "wallet_save_url",
            "wallet_object_id",
            "smartlock_code",
            "smartlock_key_id",
            "created_at",
        )
