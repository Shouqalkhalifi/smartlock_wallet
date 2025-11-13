from rest_framework.routers import DefaultRouter
from .views import SmartLockViewSet, AccessPassViewSet

router = DefaultRouter()
router.register("devices", SmartLockViewSet)
router.register("passes", AccessPassViewSet, basename="passes")

urlpatterns = router.urls
