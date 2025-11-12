from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from locks.models import AccessPass

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_wallet_link(request, booking_id: int):
    try:
        ap = AccessPass.objects.filter(
            booking_id=booking_id,
            is_active=True
        ).latest("created_at")
    except AccessPass.DoesNotExist:
        return Response({"detail": "No active access pass"}, status=404)

    return Response({
        "wallet_save_url": f"https://pay.google.com/gp/v/save/{ap.wallet_jwt}",
        "valid_from": ap.valid_from,
        "valid_to": ap.valid_to,
        "code": ap.code,
    }, status=200)
