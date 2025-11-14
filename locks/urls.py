from django.urls import path
from .views import add_lock

urlpatterns = [
    path("add/", add_lock, name="add_lock"),
]
