from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django Admin (مخفي خلف مسار مخصص)
    path(settings.ADMIN_URL, admin.site.urls),

    # الواجهة الرئيسية للموظفين
    path("", include("dashboard.urls")),

    # API Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),

    # REST APIs
    path("api/bookings/", include("bookings.urls")),
    path("api/locks/", include("locks.urls")),
    path("api/wallet/", include("walletpass.urls")),
]
