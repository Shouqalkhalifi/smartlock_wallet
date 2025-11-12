from rest_framework import serializers
from .models import SmartLock, AccessPass

class SmartLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartLock
        fields = "__all__"

class AccessPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPass
        fields = "__all__"
