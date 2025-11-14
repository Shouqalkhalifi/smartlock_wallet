from celery import shared_task
from django.utils import timezone

from locks.models import AccessPass
from locks.services import revoke_access_for_booking


@shared_task
def deactivate_expired_passes():
    """
    تعطيل صلاحيات الوصول المنتهية تلقائيًا + إلغاء PIN في TTLock
    """
    now = timezone.now()
    expired_passes = AccessPass.objects.filter(active=True, valid_to__lt=now)
    count = 0

    for ap in expired_passes:
        revoke_access_for_booking(ap.booking)
        count += 1

    return count
