from django.urls import path

from .views import CreateUser, CreateRoom, enter_room, index

app_name = "game"

urlpatterns = [
    path("", index, name='index'),
    path("user/", CreateUser.as_view()),
    path("room/<str:room_id>/", enter_room, name='enter_room'),
    path("room/", CreateRoom.as_view()),
]