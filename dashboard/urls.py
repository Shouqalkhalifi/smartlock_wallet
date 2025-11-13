from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    # قائمة الحجوزات
    path("bookings/", views.booking_list, name="booking_list"),

    # تفاصيل حجز معين
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),

    # تأكيد الحجز
    path("bookings/<int:pk>/confirm/", views.booking_confirm, name="booking_confirm"),

    # إلغاء الحجز
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
]
