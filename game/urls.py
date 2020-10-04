from django.urls import path

from .views import create_user, create_room

app_name = "game"

urlpatterns = [
    path("user/", create_user),
    path("room/", create_room),
]