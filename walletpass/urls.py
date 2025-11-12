from django.urls import path
from .views import get_wallet_link
urlpatterns = [ path("link/<int:booking_id>/", get_wallet_link) ]
