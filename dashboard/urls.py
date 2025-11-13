from django.urls import path
from . import views

urlpatterns = [
    path("", views.employee_home, name="dashboard_home"),

    # الحجوزات
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/confirm/", views.booking_confirm, name="booking_confirm"),
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),

    # الأقفال الذكية
    path("locks/", views.locks_list, name="locks_list"),
    path("wallet/", views.wallet_home, name="wallet_home"),

]
