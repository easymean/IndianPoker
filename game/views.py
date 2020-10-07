from django.shortcuts import redirect

from rest_framework.decorators import api_view
from rest_framework import serializers, status, generics
from rest_framework.response import Response

from .serializers import UserSerializer, RoomSerializer


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateRoom(generics.CreateAPIView):
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        response = super(CreateRoom, self).create(request, *args, **kwargs)
        data = response.data
        str_id = data["id"]
        return redirect("/game/" + str_id + "/")


@api_view(['DELETE'])
def delete_user(request):
    pass

@api_view(['GET'])
def enter_room(request):
    if request.method == 'GET':
        pass

@api_view(['GET'])
def exit_room(request):
    pass


