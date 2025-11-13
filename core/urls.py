from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # -------------------------------------------------
    # لوحة التحكم المخفية (Admin)
    # -------------------------------------------------
    path(settings.ADMIN_URL, admin.site.urls),

    # -------------------------------------------------
    # لوحة الموظفين (Dashboard)
    # -------------------------------------------------
    path("dashboard/", include("dashboard.urls")),

    # -------------------------------------------------
    # الواجهة الرئيسية → صفحة الحجوزات للموظف
    # -------------------------------------------------
    path("", include("dashboard.urls")),

    # -------------------------------------------------
    # API Documentation (Swagger)
    # -------------------------------------------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),

    # -------------------------------------------------
    # APIs
    # -------------------------------------------------
    path("api/bookings/", include("bookings.urls")),
    path("api/locks/", include("locks.urls")),
    path("api/wallet/", include("walletpass.urls")),
]
