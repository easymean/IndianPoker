from django.urls import path

from .views import CreateUser, CreateRoom, enter_room, index, select_room

app_name = "game"

urlpatterns = [
    path("", index, name='index'),
    path("user/", CreateUser.as_view()),
    path("choice/", select_room, name='select_room'),
    path("room/<str:room_id>/", enter_room, name='enter_room'),
    path("room/", CreateRoom.as_view()),
]