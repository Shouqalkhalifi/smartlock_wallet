from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, dashboard

router = DefaultRouter()
router.register("", BookingViewSet, basename="booking")

urlpatterns = [
    path("", dashboard, name="dashboard"),
]

urlpatterns += router.urls
