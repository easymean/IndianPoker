from django.urls import path

from . import views
app_name = "game"

urlpatterns = [
    path("", views.index, name='index'),
    path("user/", views.CreateUser.as_view()),
    path("choice/", views.select_room, name='select_room'),
    path("room/<str:room_id>/", views.enter_room, name='enter_room'),
    path("room/<str:room_id>/", views.exit_room, name='exit_room'),
    path("room/", views.CreateRoom.as_view()),
]