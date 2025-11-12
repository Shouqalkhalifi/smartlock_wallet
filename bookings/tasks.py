from celery import shared_task
from django.utils import timezone
from locks.models import AccessPass

@shared_task
def deactivate_expired_passes():
    now=timezone.now()
    qs=AccessPass.objects.filter(active=True, valid_to__lt=now)
    count=qs.update(active=False)
    return count
