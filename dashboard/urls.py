from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("booking/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("booking/<int:pk>/confirm/", views.booking_confirm, name="dashboard_booking_confirm"),
    path("booking/<int:pk>/cancel/", views.booking_cancel, name="dashboard_booking_cancel"),
]
