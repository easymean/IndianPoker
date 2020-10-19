from rest_framework import serializers

from .models import User, Room


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    nickname = serializers.CharField(max_length=100)

    def create(self, validated_data):
        user = User(**validated_data)
        user.make_user()
        return user


class RoomSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=100)

    def create(self, validated_data):
        room = Room(**validated_data)
        room.make_room()
        return room
