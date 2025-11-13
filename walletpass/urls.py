from django.urls import path
from .views import GoogleWalletPassView

urlpatterns = [
    path("create/", GoogleWalletPassView.as_view(), name="wallet-pass-create"),
]
