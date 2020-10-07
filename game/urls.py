from django.urls import path

from .views import CreateUser, create_room, CreateRoom

app_name = "game"

urlpatterns = [
    path("user/", CreateUser.as_view()),
    path("room/", CreateRoom.as_view()),
]