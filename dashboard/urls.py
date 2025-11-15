from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    # الحجوزات
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/create/", views.booking_create, name="booking_create"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/edit/", views.booking_edit, name="booking_edit"),
    path("bookings/<int:pk>/confirm/", views.booking_confirm, name="booking_confirm"),
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),

    # الأقفال الذكية
    path("locks/", views.locks_list, name="locks_list"),
    path("locks/add/", views.lock_create, name="lock_create"),   # ← تمت إضافتها هنا ✔️

    # بطاقات الدخول
    path("wallet/", views.wallet_home, name="wallet_home"),
]
