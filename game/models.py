import uuid

from utils.redis_client import r
from enum import Enum


class RoomState(int, Enum):
    EMPTY = 1
    READY = 2
    START = 3


class MessageType(int, Enum):
    ENTER = 1
    QUIT = 2
    CHAT = 3


class User:
    def __init__(self, nickname):
        self.id = uuid.uuid4()
        self.nickname = nickname
        self.ready_state = 0
        self.score = 10

    def __str__(self):
        return str(self.id)

    def make_user(self):
        hash_name = str(self.id)
        key_value = {
            "nickname": self.nickname,
            "ready_state": self.ready_state,
            "score": self.score
        }
        r.hmset(hash_name, key_value)
        r.rpush("user", hash_name);


class Room:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
        self.state = RoomState.EMPTY
        self.user_count = 0
        self.round = 0

    def __str__(self):
        return str(self.id)

    def make_room(self):
        hash_name = str(self.id)
        key_value = {
            "name": self.name,
            "state": self.state,
            "user_count":self.user_count,
            "round": self.round,
        }
        r.hmset(hash_name, key_value);
        r.rpush("room", hash_name);


def increase_user_count(room_id):
    r.hincrby(room_id, "user_count", 1)


def decrease_user_count(room_id):
    r.hdecrby(room_id, "user_count", 1)


def user_enter_room(room_id, user_id):
    hash_key = user_id
    field_value = {
            "type": MessageType.ENTER,
            "room_id" : room_id
    }
    r.hmset(hash_key, field_value)
    increase_user_count(room_id)



class InfoMessage:
    def __init__(self, room_id, sender_id):
        self.type = 0
        self.room_id = room_id
        self.sender_id = sender_id
        self.message = ""

    def enter_room(self):
        self.type = MessageType.ENTER
        self.message = f"{self.sender_id} has entered the room {self.room_id}"
        hash_map = {
            "type": self.type,
            "sender_id": self.sender_id,
            "room_id" : self.room_id
        }
        r.rpush("user_room_list", hash_map)
        self.increase_user_count()
