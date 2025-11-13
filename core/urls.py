# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # -------------------------------------------------
    # لوحة التحكم المخفية (Django Admin)
    # -------------------------------------------------
    path(settings.ADMIN_URL, admin.site.urls),

    # -------------------------------------------------
    # الواجهة الرئيسية → تحويل إلى لوحة الموظفين
    # -------------------------------------------------
    path("", include("dashboard.urls")),  # الصفحة الرئيسية للنظام

    # -------------------------------------------------
    # لوحة الموظفين (Dashboard)
    # -------------------------------------------------
    path("dashboard/", include("dashboard.urls")),

    # -------------------------------------------------
    # API Documentation (Swagger UI)
    # -------------------------------------------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),

    # -------------------------------------------------
    # REST APIs
    # -------------------------------------------------
    path("api/bookings/", include("bookings.urls")),
    path("api/locks/", include("locks.urls")),
    path("api/wallet/", include("walletpass.urls")),
]
