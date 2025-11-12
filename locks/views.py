from rest_framework import viewsets
from .models import SmartLock, AccessPass
from .serializers import SmartLockSerializer, AccessPassSerializer

class SmartLockViewSet(viewsets.ModelViewSet):
    queryset=SmartLock.objects.all()
    serializer_class=SmartLockSerializer

class AccessPassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=AccessPass.objects.all().order_by("-created_at")
    serializer_class=AccessPassSerializer
