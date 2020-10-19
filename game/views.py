from django.shortcuts import redirect, render

from rest_framework.decorators import api_view
from rest_framework import serializers, status, generics
from rest_framework.response import Response

from .models import enter_room as user_enter_room
from utils.redis_client import r

from .serializers import UserSerializer, RoomSerializer

def index(request):
    return render(request, 'game/index.html', {})


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super(CreateUser, self).create(request, *args, **kwargs)
        data = response.data
        user_id = data["id"]
        response.set_cookie("user_id", user_id)
        return response


class CreateRoom(generics.CreateAPIView):
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        response = super(CreateRoom, self).create(request, *args, **kwargs)
        data = response.data
        room_id = data["id"]
        user_id = request.COOKIES.get('user_id')
        user_enter_room(user_id=user_id, room_id=room_id)
        return response


@api_view(['GET'])
def select_room(request):
    return render(request, 'game/room_info.html', {})


@api_view(['GET'])
def enter_room(request, room_id):
    return render(request, 'game/room.html', {
        'room_id': room_id,
    })



@api_view(['GET'])
def exit_room(request):
    pass


@api_view(['DELETE'])
def delete_user(request):
    pass


