from rest_framework import serializers


class WalletUrlSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    wallet_save_url = serializers.URLField()
