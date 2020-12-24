from django.shortcuts import redirect, render

from rest_framework.decorators import api_view
from rest_framework import serializers, status, generics
from rest_framework.response import Response

from .models import enter_room as user_enter_room

from .serializers import UserSerializer, RoomSerializer


@api_view(['GET'])
def index(request):
    return render(request, 'game/index.html', {})


@api_view(['GET'])
def select_room(request):
    return render(request, 'game/room_info.html', {})


@api_view(['GET'])
def enter_room(request, room_id):
    user_id = request.COOKIES.get('user_id')
    user_enter_room(user_id=user_id, room_id=room_id) #에러 처리 확인
    return render(request, 'game/room.html', {
        'room_id': room_id,
    })


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
        return response




