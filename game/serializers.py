from rest_framework.serializers import ModelSerializer

from utils.redis_client import r

from .models import User, Room


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ["ready_state", "score"]

    def create(self, validated_data):
        user = User(**validated_data)
        hash_name = user.pk
        key_value = {
            "type": "user",
            "nickname": user.nickname,
            "ready_state": user.ready_state,
            "score": user.score
        }
        r.hmset(hash_name, key_value)
        return user

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields=["id", "group_name", "state", "round"]

    def create(self, validated_data):
        room = Room(**validated_data)
        room.make_room();
        return room