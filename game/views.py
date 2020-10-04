#api
# create user / delete user
# create room / delete room
# enter room / exit room
# start game / end game

from django.core.cache import cache

from rest_framework.decorators import api_view
from rest_framework import serializers, status
from rest_framework.response import Response

from .serializers import UserSerializer, RoomSerializer


@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_user(request):
    pass


@api_view(['POST'])
def create_room(request):
    if request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def enter_room(request):
    if request.method == 'GET':
        pass

@api_view(['GET'])
def exit_room(request):
    pass


